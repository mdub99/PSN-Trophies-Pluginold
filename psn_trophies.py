from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image, ImageDraw, ImageFont
from psnawp_api import PSNAWP
from datetime import datetime
import logging
import os


class PSNTrophiesPlugin(BasePlugin):

    def generate_image(self, plugin_settings, device_config):

        width, height = device_config.get_resolution()
        image = Image.new("RGB", (width, height), "#111111")
        draw = ImageDraw.Draw(image)

        online_id = plugin_settings.get("online_id")
        npsso = plugin_settings.get("npsso")

        # -------------------------
        # Fonts
        # -------------------------
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if not os.path.exists(font_path):
                font_path = "C:\\Windows\\Fonts\\arial.ttf"

            title_font = ImageFont.truetype(font_path, 36)
            large_font = ImageFont.truetype(font_path, 48)
            medium_font = ImageFont.truetype(font_path, 28)
            small_font = ImageFont.truetype(font_path, 22)

        except:
            title_font = ImageFont.load_default()
            large_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        trophy_colors = {
            "Platinum": "#9b59b6",
            "Gold": "#f1c40f",
            "Silver": "#bdc3c7",
            "Bronze": "#a0522d"
        }

        if not online_id or not npsso:
            draw.text(
                (50, 50),
                "Missing PSN credentials",
                fill="white",
                font=title_font
            )
            return image

        try:

            # -------------------------
            # Connect to PSN
            # -------------------------
            psnawp = PSNAWP(npsso)
            user = psnawp.user(online_id=online_id)

            summary = user.trophy_summary()

            level = summary.trophy_level
            earned = summary.earned_trophies

            total_trophies_count = (
                earned.platinum +
                earned.gold +
                earned.silver +
                earned.bronze
            )

            # -------------------------
            # HEADER
            # -------------------------
            draw.line(
                (0, 80, width, 80),
                fill="#333333",
                width=2
            )

            draw.text(
                (40, 20),
                online_id,
                fill="white",
                font=title_font
            )

            draw.text(
                (width - 250, 20),
                f"Level {level}",
                fill="white",
                font=title_font
            )

            # -------------------------
            # TROPHY TOTALS
            # -------------------------
            center_y = height // 3
            spacing = width // 4

            trophy_data = [
                ("Platinum", earned.platinum),
                ("Gold", earned.gold),
                ("Silver", earned.silver),
                ("Bronze", earned.bronze)
            ]

            for i, (label, value) in enumerate(trophy_data):

                x = spacing * i + spacing // 2

                draw.text(
                    (x - 30, center_y - 50),
                    str(value),
                    fill=trophy_colors[label],
                    font=large_font
                )

                draw.text(
                    (x - 45, center_y + 10),
                    label,
                    fill="white",
                    font=medium_font
                )

                # Progress bar
                bar_width = 80
                bar_height = 12
                bar_x = x - bar_width // 2
                bar_y = center_y + 50

                draw.rectangle(
                    (
                        bar_x,
                        bar_y,
                        bar_x + bar_width,
                        bar_y + bar_height
                    ),
                    fill="#333333"
                )

                if total_trophies_count > 0:
                    progress_width = int(
                        (value / total_trophies_count) * bar_width
                    )
                else:
                    progress_width = 0

                draw.rectangle(
                    (
                        bar_x,
                        bar_y,
                        bar_x + progress_width,
                        bar_y + bar_height
                    ),
                    fill=trophy_colors[label]
                )

            # -------------------------
            # FOOTER
            # -------------------------
            draw.line(
                (0, height - 60, width, height - 60),
                fill="#333333",
                width=2
            )

            timestamp = datetime.now().strftime("%b %d, %Y • %I:%M %p")

            draw.text(
                (40, height - 45),
                f"Last Updated: {timestamp}",
                fill="white",
                font=small_font
            )

        except Exception as e:

            logging.exception("PSN Error")

            error = str(e).lower()

            if (
                "401" in error or
                "unauthorized" in error or
                "authentication" in error or
                "npsso" in error or
                "expired" in error
            ):

                draw.text(
                    (50, 50),
                    "PSN Authentication Failed",
                    fill="#ffcc00",
                    font=title_font
                )

                draw.text(
                    (50, 110),
                    "Your NPSSO token has expired.",
                    fill="white",
                    font=medium_font
                )

                draw.text(
                    (50, 150),
                    "Please update your NPSSO token",
                    fill="white",
                    font=medium_font
                )

            else:

                draw.text(
                    (50, 50),
                    "PSN Connection Failed",
                    fill="red",
                    font=title_font
                )

                draw.text(
                    (50, 110),
                    str(e)[:90],
                    fill="white",
                    font=small_font
                )

        return image
