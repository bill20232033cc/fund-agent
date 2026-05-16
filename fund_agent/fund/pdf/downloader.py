"""下载基金年报 PDF（东方财富天天基金 + 巨潮资讯网）。"""

import logging
from pathlib import Path

import akshare as ak
import httpx

logger = logging.getLogger(__name__)

EASTMONEY_PDF_URL = "https://pdf.dfcfw.com/pdf/H2_{report_id}_1.pdf"

DEFAULT_CACHE_DIR = Path("cache/pdf")


def _find_annual_report_id(fund_code: str, year: int) -> str | None:
    """通过 akshare 查找指定基金年报的公告 ID。

    Uses akshare (synchronous) to search eastmoney fund announcements.
    """
    df = ak.fund_announcement_report_em(symbol=fund_code)
    annual = df[df["公告标题"].str.contains("年度报告") & ~df["公告标题"].str.contains("摘要")]

    for _, row in annual.iterrows():
        title = str(row["公告标题"])
        if str(year) in title:
            return str(row["报告ID"])

    # Fallback: return the latest annual report
    if len(annual) > 0:
        return str(annual.iloc[-1]["报告ID"])

    return None


async def download_pdf(
    url: str,
    dest_dir: Path | None = None,
    *,
    filename: str | None = None,
    timeout: float = 60.0,
) -> Path:
    """下载 PDF 文件到本地缓存。

    Args:
        url: PDF 下载地址。
        dest_dir: 缓存目录，默认 cache/pdf/。
        filename: 指定文件名，默认从 URL 提取。
        timeout: 下载超时（秒）。

    Returns:
        本地 PDF 文件路径。
    """
    dest_dir = dest_dir or DEFAULT_CACHE_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not filename:
        filename = url.rsplit("/", 1)[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

    dest_path = dest_dir / filename

    if dest_path.exists():
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
        dest_path.write_bytes(resp.content)

    logger.info("Downloaded: %s (%d bytes)", dest_path, dest_path.stat().st_size)
    return dest_path


async def download_annual_report(
    fund_code: str,
    year: int = 2024,
    *,
    dest_dir: Path | None = None,
) -> Path:
    """搜索并下载指定基金的年报 PDF。

    Uses akshare to find the report ID from eastmoney,
    then downloads from pdf.dfcfw.com.

    Returns:
        本地 PDF 文件路径。

    Raises:
        FileNotFoundError: 未找到年报公告。
    """
    report_id = _find_annual_report_id(fund_code, year)

    if not report_id:
        raise FileNotFoundError(f"未找到基金 {fund_code} 的 {year} 年年报")

    url = EASTMONEY_PDF_URL.format(report_id=report_id)
    logger.info("Report ID: %s -> %s", report_id, url)

    filename = f"{fund_code}_{year}_annual_report.pdf"
    return await download_pdf(url, dest_dir, filename=filename)
