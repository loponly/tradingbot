import asyncio

loop = asyncio.get_event_loop()


async def phase1(var):

    print(f'this is phase1 {var}')
    return var


async def phase2(var):
    print(f'this is phase2 {var}')
    var += 100
    return var


async def outer():
    resut1 = await phase1(2)
    print('waiting for phase 1')
    await asyncio.sleep(2)
    resut2 = await phase2(100)
    print('wating phase 2')
    await asyncio.sleep(2)
    return resut1, resut2


async def gather():
    await asyncio.gather(outer(), outer())


if __name__ == "__main__":
    # a = {'a': 'c'}
    asyncio.run(phase2(2))
