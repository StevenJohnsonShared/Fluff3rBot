# bot.py
import os
import time
import asyncio
import discord
import ImageConvert
from discord.ext import commands


# Client
client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    await client.process_commands(message)


# # # # # # # # # # # #
# Fluff3rBot commands #
# # # # # # # # # # # #


# Hello command: !hello
# Essentially a ping
@client.command(name='hello')
async def hello(context):
    await context.message.channel.send("Hi")



# Ping command: !ping
# pings to make sure the bot is working
@client.command(name='ping')
async def ping(context):
    await context.message.channel.send("Ping")



# Delete Messages: !deleteMessages {number of messages}
# used to delete specific number of messages.
@client.command(name='deleteMessages')
async def deleteMessages(context):
    # get the content of the message and split the parameters from the command.
    content = context.message.content.split(' ')

    # If the length of the message is not two or the parameter is not numeric
    # then the command is not used correctly.
    if len(content) != 2 or not content[1].isnumeric():
        await context.message.channel.send("Incorrect usage of !deleteMessage. Example: !deleteMessage {number of messages}.")
        return

    # Get the channel that the message was sent in.
    channel = context.message.channel
    # Get the number of messages specified from the channel the message was sent in.
    fetchedMessages = await channel.history(limit=int(content[1])+1).flatten()

    # For each message fetched, delete.
    for messages in fetchedMessages:
        await messages.delete()



# Gaming Train: !gaming-train {game name} or !gaming-train {game name} {roles to @}
# Used to have everyone vote for when they want to play
@client.command(name='gaming-train')
async def gamingTrain(context):
    # get content of the message
    content = context.message.content.split(' ')
    # if the length is 2 then it should just be the command and game
    if len(content) == 2:
        game = content[1]
        msg = await context.message.channel.send("Chooo Chooo, all aboard the gaming train! Next stop, {} city.\nSelect a time that works.".format(game))
    # if the length is three then it should be the command, game, and @
    elif len(content) == 3:
        game = content[1]
        role = content[2]
        msg = await context.message.channel.send("@{} Chooo Chooo, all aboard the gaming train! Next stop, {} city.\nSelect a time that works.".format(role, game))
    # else it is not used correctly
    else:
        await context.message.channel.send("Incorrect usage of !gaming-train. Example: !gaming-train {game name} or !gaming-train {game name} {roles to @}.")
        return
    # Add the reactions to the message
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '🕚', '🕛', '🌞', '🌑']
    for emoji in reactions:
        await msg.add_reaction(emoji)
    



# Who'd Be Down: !wbd {game name} or !wbd {game name} {min number of players} or !wbd {game name} {min number of players} {max number of players}
# Used to see who would be down to play a certain game.
@client.command(name='wbd')
async def wbd(context):
    # get the content of the message
    content = context.message.content.split(' ')
    # if the length is less than 2 or more than 4 then it is not used correctly
    if len(content) < 2 or len(content) > 4:
        await context.message.channel.send("Incorrect usage of !wbd. Examples:\n !wbd {game name} \n!wbd {game name} {min number of players}")
        return
    game = content[1]
    reactions = ['✔️', '❔']
    # Creating the list of gaming train message emojis
    messageReactions = []
    # Deletes message for cleaner look
    await context.message.delete()
    # if the length of content is two then it is just the command and game
    if len(content) == 2:
        msg = await context.message.channel.send("Who would be down to play {} later?".format(game))
        for emoji in reactions:
            await msg.add_reaction(emoji)
        asyncio.sleep(300)
    # else if the length is three then it is the command, game name, and minimum players
    elif len(content) == 3:
        # if the third item in the list isn't numeric then it is not used correctly
        if not content[2].isnumeric():
            await context.message.channel.send("Incorrect usage of !wbd. Examples:\n !wbd {game name} \n!wbd {game name} {min number of players}")
            return
        # Sending message to the channel with game name and number of players needed
        minimumPlayers = int(content[2])
        msg = await context.message.channel.send("Who would be down to play {}. Need at least {}.".format(game, minimumPlayers))
        # getting the message id for later
        msgId = msg.id
        # adding all the emojis
        for emoji in reactions:
            await msg.add_reaction(emoji)
        # give it time to finish adding emojis
        time.sleep(2)
        # wait for ten mins checking if there are enough people wanting to play every second
        for i in range(600):
            msg = await context.channel.fetch_message(msgId)
            messageReactions = msg.reactions
            # if there are enough players break the loop and print that there are enough players
            if messageReactions[0].count >= minimumPlayers+1:
                await msg.edit(content=msg.content + " Looks like we have enough players.")
                # await context.message.channel.send("Looks like we have enough players.")
                break
            asyncio.sleep(1)
        # if the minimum number of players is not hit after 10 mins then break return to avoid the 
        # gaming train
        return
    else:
        await context.message.channel.send("Incorrect usage of !wbd. Examples:\n !wbd {game name} \n!wbd {game name} {min number of players}")
        return
    # changing the context message content to the gaming train command
    context.message.content = "!gaming-train {}".format(game)
    # two variables checking if there are at least two people wanting to play
    # if there isn't a minimum number of people then it will see who wants to play
    peoplePlaying = ''
    peopleList = []
    # looping over all the reactions
    for reaction in messageReactions:
        # iterate over the users that clicked the reaction
        async for user in reaction.users():
            # if the user is not the bot or already accounted for then add them
            if user != client.user and user.mention not in peoplePlaying:
                peoplePlaying += '{}'.format(user.mention)
                peopleList.append(user)
    # if at least two people want to play then then run the gaming train.
    if(len(peopleList) >= 2):
        await context.message.channel.send(peoplePlaying)
        await client.get_command('gaming-train').invoke(context)



# Move: !move {channel to move to} {number of messages}
# Used to move messages from one channel to another.
@client.command(name='move')
async def move(context):

    if "mod" not in [y.name.lower() for y in context.message.author.roles]:
        await context.message.delete()
        await context.channel.send("{} you do not have the permissions to move messages.".format(context.message.author))
        return

    # get the content of the message
    content = context.message.content.split(' ')
    # if the length is not three the command was used incorrectly
    if len(content) != 3 or not content[2].isnumeric():
        await context.message.channel.send("Incorrect usage of !move. Example: !move {channel to move to} {number of messages}.")
        return
    # channel that it is going to be posted to
    channelTo = content[1]
    # get the number of messages to be moved (including the command message)
    numberOfMessages = int(content[2]) + 1
    # get a list of the messages
    fetchedMessages = await context.channel.history(limit=numberOfMessages).flatten()
    
    # delete all of those messages from the channel
    for i in fetchedMessages:
        await i.delete()

    # invert the list and remove the last message (gets rid of the command message)
    fetchedMessages = fetchedMessages[::-1]
    fetchedMessages = fetchedMessages[:-1]
    print(fetchedMessages)

    # Loop over the messages fetched
    for messages in fetchedMessages:
        # get the channel object for the server to send to
        channelTo = discord.utils.get(messages.guild.channels, name=channelTo)

        # if the message is embeded already
        if messages.embeds:
            # set the embed message to the old embed object
            embedMessage = messages.embeds[0]
        # else
        else:
            # Create embed message object and set content to original
            embedMessage = discord.Embed(
                        description = messages.content
                        )
            # set the embed message author to original author
            embedMessage.set_author(name=messages.author, icon_url=messages.author.avatar_url)
            # if message has attachments add them
            if messages.attachments:
                for i in messages.attachments:
                    embedMessage.set_image(url = i.proxy_url)

        # Send to the desired channel
        await channelTo.send(embed=embedMessage)



# Convert Image to ASCII: !ascii
# Gets the picture from the previous image and turns it to ascii art
@client.command(name='ascii')
async def ConvertToAscii(context):
    # Get the last two messages sent in chat.
    fetchedMessages = await context.channel.history(limit=2).flatten()
    # If the message before the command does not have an image return error.
    imageMessage = fetchedMessages[1]

    # If the message has no attachments
    if not imageMessage.attachments:
        errorMessage = await context.channel.send("There was no image to convert.")
        # Wait for 4 seconds then delete the command and the error message.
        return
    # Try to convert the image
    try:
        messageAttachments = imageMessage.attachments
        for attachment in messageAttachments:
            convertedAsciiImage = ImageConvert.convert(attachment.proxy_url)
            convertedAsciiImageLarge = ImageConvert.convertLarge(attachment.proxy_url)
            with open("AsciiArt.txt", 'rb') as file:
                await context.channel.send("Behold:", file=discord.File(file, "AsciiArt.txt"))
            with open("AsciiArtLarge.txt", 'rb') as file:
                await context.channel.send(file=discord.File(file, "AsciiArtLarge.txt"))
    except Exception as e:
        # If there was an error send an error message
        await context.channel.send(str(e))
        errorMessage = await context.channel.send("Attachment is not a valid image.")
        return



# Nicolas: !nicolas
# sends a picture of Nocials Cage
@client.command(name='nicolas')
async def nick(context):
    await context.message.delete()
    embeddedMessage = discord.Embed()
    embeddedMessage.set_author(name='Nicolas Cage', icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Nicolas_Cage_Deauville_2013.jpg/220px-Nicolas_Cage_Deauville_2013.jpg')
    embeddedMessage.set_image(url='https://upload.wikimedia.org/wikipedia/commons/f/f3/Nicolas_Cage_-_66%C3%A8me_Festival_de_Venise_%28Mostra%29.jpg')

    await context.message.channel.send(embed=embeddedMessage)



# Run the bot
client.run(os.environ['token'])
