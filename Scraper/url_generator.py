import time

start = "https://www.shipspotting.com/photos/"
id = 3548586
start_time = time.time()
with open("./urls.csv", "w") as fp:
      fp.write("url,id\n")
      for i in range(2200000, 2300000):#3548569):
            fp.write(f"{start}{id-i},{id-i}\n")
end = time.time() - start_time
print(f"Elapsed time: {end} seconds")

# 3185 escluso error gia processati