#!/usr/bin/env python3
"""Capture Google Earth screenshots for polygons defined in a KML file using Playwright."""

import argparse
import asyncio
import os

import geopandas as gpd
from playwright.async_api import async_playwright

DEBUG = False


async def click_at_coordinates(page, x: int, y: int, sleep: float = 1.0) -> None:
    """Click at the given coordinates on the page."""
    await page.mouse.click(x, y)
    await page.wait_for_timeout(int(sleep * 1000))


async def move_cursor_to_coordinates(page, x: int, y: int, sleep: float = 1.0) -> None:
    """Move the cursor to the given coordinates on the page."""
    await page.mouse.move(x, y)
    await page.wait_for_timeout(int(sleep * 1000))


async def complete_file_upload(page, file_path: str) -> None:
    """Upload the KML file using Playwright's file chooser event."""
    abs_path = os.path.abspath(file_path)
    async with page.expect_file_chooser() as fc:
        await click_at_coordinates(page, 158, 273)  # Select "Import KML file"
        file_chooser = await fc.value
    await file_chooser.set_files(abs_path)
    await page.wait_for_timeout(1000)


async def screenshot_polygons(kml_path: str, output_dir: str, wait: int = 10) -> None:
    """Generate a screenshot for each polygon in the KML file."""
    gdf = gpd.read_file(kml_path, driver="KML")
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 3840, "height": 2160})
        page = await context.new_page()

        await page.goto("https://earth.google.com/web/")
        await page.wait_for_timeout(5000)
        await click_at_coordinates(page, 76, 9)  # Open the file menu
        await complete_file_upload(page, kml_path)
        await click_at_coordinates(page, 276, 206)  # Dismiss the popup
        await click_at_coordinates(page, 390, 2100)  # Open layer settings
        await click_at_coordinates(page, 600, 890)  # Select satellite view
        await click_at_coordinates(page, 600, 1094)  # Select clean view
        await click_at_coordinates(page, 580, 1540)  # Disable 3D buildings
        await click_at_coordinates(page, 608, 798)  # Close layer settings
        await click_at_coordinates(page, 530, 90)  # Shrink the menu bar
        await click_at_coordinates(page, 3811, 30)  # Open profile menu
        await click_at_coordinates(page, 3508, 186)  # Open settings
        await click_at_coordinates(page, 2167, 184)  # Disable flight animations
        await click_at_coordinates(page, 1994, 643)  # Max out rendering quality
        await click_at_coordinates(page, 2193, 2024)  # Close settings
        # await click_at_coordinates(page, 27, 141)  # Expand the folder
        # await click_at_coordinates(page, 281, 164)  # Unhide folder
        for i in range(len(gdf)):
            polygon_y = 195 + int(i * 1343 / 28)
            await click_at_coordinates(page, 158, polygon_y, sleep=0.1)
            await click_at_coordinates(
                page, 158, polygon_y
            )  # double click to go to polygon
            await click_at_coordinates(page, 3802, 101)  # Close the polygon info
            await move_cursor_to_coordinates(page, 283, 145)
            await click_at_coordinates(page, 283, 145)  # Hide all polygons
            await click_at_coordinates(page, 327, 1109)  # Close the kml menu

            outfile = os.path.join(output_dir, f"polygon_{i}_raw.png")
            await page.screenshot(path=outfile)
            print(f"Saved {outfile}")

            await click_at_coordinates(page, 14, 1109)  # Open the kml menu
            await click_at_coordinates(page, 158, polygon_y, sleep=0.1)
            await click_at_coordinates(
                page, 158, polygon_y
            )  # double click to go to polygon
            await click_at_coordinates(page, 3802, 104)  # Close the polygon info
            await move_cursor_to_coordinates(page, 283, 145)
            await click_at_coordinates(page, 283, 145)  # Unhide all polygons
            await click_at_coordinates(page, 327, 1109)  # Close the kml menu

            outfile = os.path.join(output_dir, f"polygon_{i}_mask.png")
            await page.screenshot(path=outfile)
            print(f"Saved {outfile}")

            await click_at_coordinates(page, 14, 1109)  # Open the kml menu
            # await move_cursor_to_coordinates(
            #     page, 283, polygon_y
            # )  # Hover the hide button
            # await click_at_coordinates(page, 283, polygon_y)  # Hide the polygon

        if DEBUG:
            outfile = os.path.join(output_dir, "debug.png")
            await page.screenshot(path=outfile)
            print(f"Saved {outfile}")
            print("Exiting due to debug mode.")
            await browser.close()
            return

        await browser.close()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture Google Earth screenshots for polygons in a KML file"
    )
    parser.add_argument("--kml", required=True, help="Path to the KML file")
    parser.add_argument(
        "--output", required=True, help="Directory to store screenshots"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=10,
        help="Seconds to wait after moving the map before taking a screenshot",
    )

    args = parser.parse_args()
    await screenshot_polygons(args.kml, args.output, wait=args.wait)


if __name__ == "__main__":
    asyncio.run(main())
