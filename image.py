import queue
import PIL.Image
import PIL.ImageDraw
import io
import discord
import time


async def mandelbrot(n=10):
    start = time.time()
    max_size = 500
    imageArray = []
    sizeone = (max_size-1)
    ratio_i = int(255/n)
    pre_z = complex(0, 0)
    for y in range(max_size):
        for x in range(max_size):
            z = pre_z
            c = complex(2.1*x/sizeone-1.5, 2.1*y/sizeone-1)
            i = 0
            while (i < n) and abs(z) < 4:
                i += 1
                z = z*z+c
            level = int(i*ratio_i)
            imageArray.append((level, level, level))
    checkpoint = time.time() - start
    image = PIL.Image.new("RGB", (max_size, max_size))
    image.putdata(imageArray)
    print(checkpoint)
    file = io.BytesIO()
    image.save(file, "PNG")
    file = io.BytesIO(file.getvalue())
    dfile = discord.File(file, "image.png")
    passed = str(time.time()-start)[0:6]
    return "Terminé en {}s".format(passed), dfile
