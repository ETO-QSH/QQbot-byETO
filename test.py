#!/usr/bin/env python3


at_me = on_message(rule=to_me())

@at_me.handle()
async def at_bot(bot: Bot, event: Event):
    if '<le>[at:qq=3078491964' in str(event.get_log_string()):
        await at_me.finish("꒰ঌ( ⌯' '⌯)໒꒱")