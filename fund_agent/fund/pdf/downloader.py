"""基金文档仓库内部使用的年报 PDF 下载 helper。

当前模块只负责定位公告并下载 PDF 到本地缓存，不再作为上层公共文档读取契约。
"""

import asyncio
import logging
from pathlib import Path

import akshare as ak
import httpx

logger = logging.getLogger(__name__)

EASTMONEY_PDF_URL = "https://pdf.dfcfw.com/pdf/H2_{report_id}_1.pdf"

DEFAULT_CACHE_DIR = Path("cache/pdf")
__all__: list[str] = []


def _find_annual_report_id(fund_code: str, year: int) -> str | None:
    """通过 akshare 查找指定基金年报公告 ID。

    Args:
        fund_code: 基金代码。
        year: 报告年份。

    Returns:
        命中时返回公告 ID；未命中时返回 ``None``。

    Raises:
        Exception: 允许 akshare 查询异常直接传播。
    """
    df = ak.fund_announcement_report_em(symbol=fund_code)
    annual = df[df["公告标题"].str.contains("年度报告") & ~df["公告标题"].str.contains("摘要")]

    for _, row in annual.iterrows():
        title = str(row["公告标题"])
        if str(year) in title:
            return str(row["报告ID"])

    return None


async def _download_pdf(
    url: str,
    dest_dir: Path | None = None,
    *,
    filename: str | None = None,
    timeout: float = 60.0,
    force_refresh: bool = False,
) -> Path:
    """下载 PDF 文件到本地缓存。

    Args:
        url: PDF 下载地址。
        dest_dir: 缓存目录，默认 cache/pdf/。
        filename: 指定文件名，默认从 URL 提取。
        timeout: 下载超时（秒）。
        force_refresh: 为 ``True`` 时即使缓存存在也重新下载。

    Returns:
        本地 PDF 文件路径。

    Raises:
        httpx.HTTPError: 下载失败时抛出。
        OSError: 写入本地缓存失败时抛出。
    """
    dest_dir = dest_dir or DEFAULT_CACHE_DIR
    await asyncio.to_thread(dest_dir.mkdir, parents=True, exist_ok=True)

    if not filename:
        filename = url.rsplit("/", 1)[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

    dest_path = dest_dir / filename

    if await asyncio.to_thread(dest_path.exists) and not force_refresh:
        logger.info("PDF already cached: %s", dest_path)
        return dest_path

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36",
    }

    logger.info("Downloading PDF: %s -> %s", url, dest_path)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        # PDF 写盘是阻塞文件 I/O，需要放到线程中执行，避免卡住异步调用链。
        await asyncio.to_thread(dest_path.write_bytes, resp.content)

    file_stat = await asyncio.to_thread(dest_path.stat)
    logger.info("Downloaded: %s (%d bytes)", dest_path, file_stat.st_size)
    return dest_path


async def _download_annual_report_pdf(
    fund_code: str,
    year: int = 2024,
    *,
    dest_dir: Path | None = None,
    force_refresh: bool = False,
) -> Path:
    """搜索并下载指定基金的年报 PDF。

    该函数是 `fund_agent.fund.documents` 仓库内部 helper。

    Args:
        fund_code: 基金代码。
        year: 报告年份。
        dest_dir: 本地缓存目录。
        force_refresh: 为 ``True`` 时跳过本地 PDF 缓存重新下载。

    Returns:
        本地 PDF 文件路径。

    Raises:
        FileNotFoundError: 未找到年报公告。
        httpx.HTTPError: 下载失败时抛出。
        OSError: 写入本地缓存失败时抛出。
    """
    # akshare 查询是同步阻塞调用，这里显式放入线程执行。
    report_id = await asyncio.to_thread(_find_annual_report_id, fund_code, year)

    if not report_id:
        raise FileNotFoundError(f"未找到基金 {fund_code} 的 {year} 年年报")

    url = EASTMONEY_PDF_URL.format(report_id=report_id)
    logger.info("Report ID: %s -> %s", report_id, url)

    filename = f"{fund_code}_{year}_annual_report.pdf"
    return await _download_pdf(
        url,
        dest_dir,
        filename=filename,
        force_refresh=force_refresh,
    )
