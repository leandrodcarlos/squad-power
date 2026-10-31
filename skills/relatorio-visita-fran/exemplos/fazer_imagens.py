"""Gera 3 imagens ilustrativas (desenhos rotulados) para o exemplo. Dados fictícios."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PASTA = Path(__file__).resolve().parent


def fonte(tam):
    for nome in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nome, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def base(rotulo):
    img = Image.new("RGB", (640, 480), "#EEF2F1")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 639, 479], outline="#1F4E3D", width=6)
    d.text((24, 20), "IMAGEM ILUSTRATIVA (exemplo fictício)", fill="#6B7A75", font=fonte(18))
    d.text((24, 430), rotulo, fill="#1F4E3D", font=fonte(30))
    return img, d


def termometro():
    img, d = base("Termômetro da câmara fria: 9 °C")
    d.rounded_rectangle([150, 80, 230, 360], 40, fill="white", outline="#333", width=5)
    d.ellipse([130, 320, 250, 420], fill="#C0392B", outline="#333", width=5)
    d.rectangle([178, 150, 202, 340], fill="#C0392B")
    d.rectangle([300, 140, 560, 300], fill="#1B1B1B")
    d.text((330, 175), "9 °C", fill="#FF6B5A", font=fonte(80))
    return img


def lixeira():
    img, d = base("Lixeira sem tampa na produção")
    d.polygon([(230, 160), (410, 160), (390, 380), (250, 380)], fill="#8FA39B", outline="#333")
    d.ellipse([220, 140, 420, 180], fill="#5C6E67", outline="#333", width=4)
    for x in (270, 320, 360):
        d.line([(x, 175), (x + 10, 370)], fill="#6F8279", width=4)
    d.text((440, 150), "sem tampa", fill="#C0392B", font=fonte(30))
    d.line([(430, 165), (400, 160)], fill="#C0392B", width=5)
    return img


def touca():
    img, d = base("Manipuladora sem touca, com anel e brinco")
    d.ellipse([250, 90, 390, 250], fill="#E8BFA0", outline="#333", width=4)
    d.rectangle([220, 250, 420, 400], fill="#F5F5F5", outline="#333", width=4)
    d.ellipse([240, 160, 262, 190], outline="#D4AF37", width=5)
    d.text((440, 140), "sem touca", fill="#C0392B", font=fonte(30))
    d.text((440, 190), "anel e brinco", fill="#C0392B", font=fonte(30))
    return img


if __name__ == "__main__":
    termometro().save(PASTA / "foto-termometro-9c.png")
    lixeira().save(PASTA / "foto-lixeira-sem-tampa.png")
    touca().save(PASTA / "foto-sem-touca.png")
    print("ok")
