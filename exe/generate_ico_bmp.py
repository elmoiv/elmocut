from PIL import Image

img = Image.open("app.png")

# Convert to icon
img = img.resize((256, 256))
img.save('icon.ico', sizes=[(256, 256)])

# Convert to bitmap
img = Image.open("app.png")
# img.convert("RGBA")
## Add white background
new_image = Image.new("RGBA", img.size, "WHITE")
new_image.paste(img, (0, 0), img)
new_image.convert('RGBA')
new_image = new_image.resize((55, 55))
## Save as bmp
new_image.save('setup_img.bmp')