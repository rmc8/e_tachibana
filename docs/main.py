from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

from html_to_markdown import convert as render_markdown
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CaptureConfig:
    source_url: str
    output_path: Path
    frame_id: str = "f_text"
    wait_seconds: int = 10
    headless: bool = True


def parse_args() -> CaptureConfig:
    parser = argparse.ArgumentParser(
        description="Capture the mfds reference frame (#f_text) and export Markdown."
    )
    parser.add_argument(
        "--source",
        default="https://www.e-shiten.jp/e_api/mfds_json_api_refference.html",
        help="URL that embeds the #f_text frame (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("md/mfds_json_api_reference.md"),
        help="Markdown output path, relative to this script (default: %(default)s)",
    )
    parser.add_argument(
        "--frame-id",
        default="f_text",
        help="Frame ID that contains the document body (default: %(default)s)",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=10,
        help="Implicit wait time in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome in headless mode.",
    )
    args = parser.parse_args()
    output_path = (Path(__file__).parent / args.output).resolve()
    return CaptureConfig(
        source_url=args.source,
        output_path=output_path,
        frame_id=args.frame_id,
        wait_seconds=args.wait,
        headless=args.headless,
    )


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def create_driver(headless: bool) -> Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    LOGGER.debug("Launching ChromeDriver (headless=%s)", headless)
    return Chrome(service=Service(ChromeDriverManager().install()), options=options)


def capture_frame_html(driver: Chrome, config: CaptureConfig) -> str:
    LOGGER.info("Loading %s", config.source_url)
    driver.get(config.source_url)
    driver.implicitly_wait(config.wait_seconds)
    frame = driver.find_element(By.ID, config.frame_id)
    driver.switch_to.frame(frame)
    LOGGER.debug("Entered frame #%s", config.frame_id)
    return driver.page_source


def save_markdown(markdown: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")
    LOGGER.info("Wrote Markdown to %s", destination)


def run_capture(config: CaptureConfig) -> None:
    driver = create_driver(config.headless)
    try:
        html = capture_frame_html(driver, config)
        md = render_markdown(html)
        save_markdown(md, config.output_path)
    finally:
        LOGGER.debug("Closing ChromeDriver")
        driver.quit()


def main() -> None:
    configure_logging()
    config = parse_args()
    LOGGER.debug("Resolved config: %s", config)
    run_capture(config)


if __name__ == "__main__":
    main()
