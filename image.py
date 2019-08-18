import queue
import PIL.Image
import PIL.ImageDraw
import io
import discord
import time
import threading
import queue

mandelbrot_in_q = queue.Queue(5)
mandelbrot_out_q = queue.Queue(5)


def mandelbrot_run(n, message, sent_message):
    start = time.time()
    max_size = 500
    imageArray = []
    sizeone = (max_size-1)
    ratio_i = int(255/n)
    pre_z = complex(0, 0)
    print("entering loop")
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
    finished = time.time()-start
    mandelbrot_out_q.put((dfile, message, sent_message, finished))
    time.sleep(1)


async def mandelbrot(n, message, sent_message, client):
    mandelbrot_in_q.put((n, message, sent_message))
    mandelbrot_t = threading.Thread(
        target=mandelbrot_run, args=(n, message, sent_message))
    mandelbrot_t.start()

    client.loop.create_task(mandelbrot_loop(client))


async def mandelbrot_loop(client):
    # print(mandelbrot_in_q)
    # if not mandelbrot_in_q.empty():
    #    print(mandelbrot_in_q.get())
    if not mandelbrot_out_q.empty():
        q = mandelbrot_out_q.get()
        if q == None:
            return
        else:
            dfile, message, sent_message, finished = q
            finished = str(finished)[:5]
            await sent_message.delete()
            await message.channel.send("Done in {}s".format(finished), file=dfile)
    else:
        client.loop.create_task(mandelbrot_loop(client))
