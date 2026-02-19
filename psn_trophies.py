from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image, ImageDraw, ImageFont
from psnawp_api import PSNAWP
from datetime import datetime
import os


class PSNTrophiesPlugin(BasePlugin):

    def generate_image(self, plugin_settings, device_config):

        width, height = device_config.get_resolution()
        image = Image.new("RGB", (width, height), "#111111")  # dark background
        draw = ImageDraw.Draw(image)

        online_id = plugin_settings.get("online_id")
        npsso = plugin_settings.get("npsso")

        # ---- Fonts ----
        # Try loading a TrueType font for larger sizes
        try:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if not os.path.exists(font_path):
                font_path = "C:\\Windows\\Fonts\\arial.ttf"  # Windows fallback

            title_font = ImageFont.truetype(font_path, 36)  # username, level
            large_font = ImageFont.truetype(font_path, 48)  # trophy numbers
            small_font = ImageFont.truetype(font_path, 24)  # footer
        except:
            title_font = ImageFont.load_default()
            large_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Trophy colors
        colors = {
            "Platinum": "#9b59b6",  # purple
            "Gold": "#f1c40f",
            "Silver": "#bdc3c7",
            "Bronze": "#a0522d"
        }

        if not online_id or not npsso:
            draw.text((50, 50), "Missing PSN credentials", fill="white", font=title_font)
            return image

        try:
            psnawp = PSNAWP(npsso)
            user = psnawp.user(online_id=online_id)
            summary = user.trophy_summary()

            level = summary.trophy_level
            earned = summary.earned_trophies

            # ---- HEADER ----
            draw.line((0, 80, width, 80), fill="#333333", width=2)
            draw.text((40, 20), online_id, fill="white", font=title_font)
            draw.text((width - 250, 20), f"Level {level}", fill="white", font=title_font)

            # ---- TROPHY SECTION ----
            center_y = height // 2
            spacing = width // 4

            trophy_data = [
                ("Platinum", earned.platinum),
                ("Gold", earned.gold),
                ("Silver", earned.silver),
                ("Bronze", earned.bronze)
            ]

            for i, (label, value) in enumerate(trophy_data):
                x = spacing * i + spacing // 2

                # Large colored number
                draw.text((x - 25, center_y - 50), str(value), fill=colors[label], font=large_font)

                # Label underneath
                draw.text((x - 40, center_y + 10), label, fill="white", font=title_font)

            # ---- FOOTER ----
            draw.line((0, height - 60, width, height - 60), fill="#333333", width=2)
            timestamp = datetime.now().strftime("%I:%M %p")
            draw.text((40, height - 45), f"Last Updated: {timestamp}", fill="white", font=small_font)

        except Exception as e:
            draw.text((50, 50), "PSN Connection Failed", fill="white", font=title_font)
            draw.text((50, 120), str(e)[:60], fill="white", font=title_font)

        return image

