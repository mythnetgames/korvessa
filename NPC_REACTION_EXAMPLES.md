# NPC Reaction Examples and Templates

This document provides ready-to-use reaction configurations for common NPC archetypes.

## Generic Greeting NPC

```
# A friendly person who greets visitors

@npc-react greeter=hello/say Hello there! Welcome!
@npc-react greeter=hello/emote nods warmly
@npc-react greeter=hi/say Hey, how can I help you?
@npc-react greeter=greetings/emote smiles and waves
@npc-react greeter=how are you/say I'm doing great, thanks for asking!
@npc-react greeter=what's up/say Not much, just passing the time here.
@npc-react greeter=name/say You can call me friend, what's yours?
```

## Street Vendor

```
# A merchant selling goods in the market

@npc-react vendor=hello/say Ah, a customer! Welcome to my stall.
@npc-react vendor=hello/emote arranges the wares on display
@npc-react vendor=wares/say I've got the finest goods in the market!
@npc-react vendor=price/say What are you interested in? I'll give you a fair price.
@npc-react vendor=quality/say I only sell the best merchandise, friend.
@npc-react vendor=discount/say Can't do discounts, but I promise fair prices.
@npc-react vendor=expensive/say You get what you pay for, quality costs.
@npc-react vendor=buy/say Excellent choice! That'll be a fair price.
@npc-react vendor=interested/say Come take a look, you might find something you like.
```

## Suspicious Guard

```
# A wary guard that's suspicious of strangers

@npc-react guard=hello/say Watch yourself, I'm keeping an eye on you.
@npc-react guard=hello/emote eyes you suspiciously
@npc-react guard=who/say That's none of your business, stranger.
@npc-react guard=who are you/say I'm the one asking the questions here.
@npc-react guard=why/say Might be watching for troublemakers like you.
@npc-react guard=trouble/say What kind of trouble are you looking for?
@npc-react guard=threat/pose raises hand to weapon
@npc-react guard=leave/say That's the smartest thing I've heard all day.
@npc-react guard=business/say State your business and move along.
```

## Friendly Bartender

```
# A welcoming bartender who enjoys conversation

@npc-react bartender=hello/say Welcome in! What can I get you?
@npc-react bartender=hello/emote wipes down the bar
@npc-react bartender=drink/say What's your pleasure? I've got everything.
@npc-react bartender=drink/say A drink, coming right up!
@npc-react bartender=strong/say I've got just the thing, strong stuff!
@npc-react bartender=news/say Word around town is things are getting interesting.
@npc-react bartender=quiet/emote chuckles and nods
@npc-react bartender=rough day/say I hear you. Rough times for everyone lately.
@npc-react bartender=thanks/say Don't mention it, that's what I'm here for!
```

## Weary Homeless Person

```
# A down-on-their-luck homeless person

@npc-react homeless=hello/say Huh? Oh, hello there.
@npc-react homeless=hello/emote looks up wearily
@npc-react homeless=help/say Help? I could use some, friend.
@npc-react homeless=spare/say A spare coin would be welcome, if you've got it.
@npc-react homeless=food/emote's stomach rumbles audibly
@npc-react homeless=sorry/say Nothing for you to be sorry about, friend.
@npc-react homeless=why/say Fallen on hard times, that's all.
@npc-react homeless=why/say Life's been unkind, but I carry on.
@npc-react homeless=news/say Haven't heard much, stuck here in the cold.
```

## Intense Scholar

```
# An intellectual obsessed with knowledge

@npc-react scholar=hello/say Ah, a visitor! I'm quite absorbed in my studies.
@npc-react scholar=hello/emote looks up from a thick book
@npc-react scholar=knowledge/say Knowledge is power, the greatest power there is!
@npc-react scholar=book/say This? A masterwork of philosophy and reason.
@npc-react scholar=learn/say Excellent! I love discussing ideas with curious minds.
@npc-react scholar=why/say Why? That's always the most important question!
@npc-react scholar=theory/emote eyes light up with excitement
@npc-react scholar=interesting/say You've touched on a fascinating subject!
@npc-react scholar=question/say Ah, the pursuit of truth! I respect that.
```

## Paranoid Conspiracy Theorist

```
# A nervous person convinced everyone is watching

@npc-react paranoid=hello/emote glances around nervously
@npc-react paranoid=hello/say Keep your voice down! They might be listening!
@npc-react paranoid=listening/say They're always listening, you never know who.
@npc-react paranoid=why/say Because they want to control us, that's why!
@npc-react paranoid=who/say I can't say names, they might hear!
@npc-react paranoid=safe/say Nowhere is truly safe, but this spot is better than most.
@npc-react paranoid=crazy/say Mad? Or just aware of the truth?
@npc-react paranoid=help/say Help? Be careful who you ask, friend.
```

## Street Urchin

```
# A young street child

@npc-react urchin=hello/say Hiya, got any coin?
@npc-react urchin=hello/emote eyes you curiously
@npc-react urchin=coin/say A copper? Would make my day!
@npc-react urchin=coin/say Help a kid out, yeah?
@npc-react urchin=food/emote's eyes light up at the mention of food
@npc-react urchin=hungry/say Always hungry on the streets.
@npc-react urchin=news/say I hear stuff sometimes, hanging around.
@npc-react urchin=want/say Lots of things I want. Most I'll never get.
@npc-react urchin=sorry/say Don't be sorry, just happens sometimes.
```

## Tough Gang Member

```
# A street gang enforcer

@npc-react gang=hello/say What are you looking at?
@npc-react gang=hello/emote cracks knuckles menacingly
@npc-react gang=territory/say This is OUR territory, friend. Remember that.
@npc-react gang=problem/emote steps closer, eyes narrowing
@npc-react gang=respect/say You respect us, we respect you. Simple.
@npc-react gang=tough/say Yeah, I am. And I'm just getting started.
@npc-react gang=why/say Why? Because I can, that's why.
@npc-react gang=business/say You got business here or not?
@npc-react gang=smart/say Smart move, knowing your place.
```

## Healing Priestess

```
# A spiritual healer

@npc-react priestess=hello/say Welcome, seeker. I sense you carry burdens.
@npc-react priestess=hello/emote's eyes glow with inner light
@npc-react priestess=heal/say I feel the wounds of your spirit.
@npc-react priestess=pain/say All pain has purpose, though it's hard to see.
@npc-react priestess=blessing/say May you find peace and clarity.
@npc-react priestess=prayer/emote begins a soft, melodic chant
@npc-react priestess=spirit/say The spirits speak to those who listen.
@npc-react priestess=help/say I offer what aid I can to those who seek it.
@npc-react priestess=faith/say Faith is the foundation of all healing.
```

## Worn-Out Soldier

```
# A veteran bearing the scars of war

@npc-react soldier=hello/say Soldier. You look like you've seen action too.
@npc-react soldier=hello/emote adjusts armor with practiced ease
@npc-react soldier=war/say War changes a person. Not always for the better.
@npc-react soldier=battle/say Too many battles. They blur together now.
@npc-react soldier=why/say Orders. That's all. I follow orders.
@npc-react soldier=injury/emote winces slightly at old wounds
@npc-react soldier=rest/say Rest? I haven't rested in years.
@npc-react soldier=duty/say Duty is all that keeps me going now.
@npc-react soldier=glory/say Glory? There's no glory in war. Just survival.
```

## Cautious Alchemist

```
# A secretive alchemist

@npc-react alchemist=hello/say Welcome, but keep your distance from my work.
@npc-react alchemist=hello/emote gestures around at bubbling potions
@npc-react alchemist=potion/say Potions are not toys, handle with care.
@npc-react alchemist=what/say What I do here is best left unexplained.
@npc-react alchemist=smell/emote wrinkles nose at a strange odor
@npc-react alchemist=danger/say Yes, what I do is quite dangerous.
@npc-react alchemist=spell/say I'm no wizard, but my concoctions work.
@npc-react alchemist=help/say I help those who understand the value of my work.
@npc-react alchemist=why/say Why? That's a question best left unanswered.
```

## Cheerful Musician

```
# An upbeat musician

@npc-react musician=hello/say Hey there, friend! Music makes the world better!
@npc-react musician=hello/emote strums an instrument cheerfully
@npc-react musician=music/say Music is the language of the soul!
@npc-react musician=song/say Want to hear a tune? I've got a few!
@npc-react musician=sad/say Music can lift any sadness, trust me!
@npc-react musician=dance/say Come on, let's have some fun!
@npc-react musician=talent/say Just years of practice and love for the craft!
@npc-react musician=performance/emote grins and bows dramatically
@npc-react musician=play/say Always happy to play for a good crowd!
```

## Grumpy Old Man

```
# An irritable elderly person

@npc-react old_man=hello/say What do you want? Speak up, I'm not getting younger!
@npc-react old_man=hello/emote grumbles and waves dismissively
@npc-react old_man=young/say You kids don't know how good you have it!
@npc-react old_man=back/say Back in my day, things were better!
@npc-react old_man=story/say Got plenty of stories, most you won't believe.
@npc-react old_man=why/say Why? Because that's how things are, that's why!
@npc-react old_man=respect/say Show some respect to your elders!
@npc-react old_man=quiet/emote mutters something under breath
@npc-react old_man=leave/say Don't let the door hit you on the way out!
```

## Mysterious Stranger

```
# An enigmatic person

@npc-react stranger=hello/say We haven't met before, have we?
@npc-react stranger=hello/emote studies you carefully
@npc-react stranger=who/say Ah, now that's a good question.
@npc-react stranger=who are you/say The answer to that depends on who's asking.
@npc-react stranger=why/say Everyone's here for a reason, what's yours?
@npc-react stranger=secret/emote glances around cautiously
@npc-react stranger=business/say Perhaps we can be of use to each other.
@npc-react stranger=trust/say Trust is earned, not given.
@npc-react stranger=story/say I've got stories, but not all are mine to tell.
```

## Quick Copy-Paste Template

Here's a blank template you can use to create your own:

```
# [NPC Name] - [Description]

@npc-react [npc_name]=[trigger]/say [response]
@npc-react [npc_name]=[trigger]/emote [action]
@npc-react [npc_name]=[trigger]/pose [action]
```

## Advanced Reaction Tips

### Multiple Responses for Variation

Add multiple reactions to the same trigger for different responses:

```
@npc-react vendor=hello/say Hi there!
@npc-react vendor=hello/say Welcome, welcome!
@npc-react vendor=hello/emote looks up and smiles
@npc-react vendor=hello/emote tips their hat to you
```

### Trigger Chains

Create related triggers that build on each other:

```
@npc-react scholar=hello/say Greetings, seeker of knowledge!
@npc-react scholar=knowledge/say Ah yes, knowledge is my passion!
@npc-react scholar=science/say The scientific method has revolutionized understanding!
@npc-react scholar=magic/say Magic and science are not so different...
```

### Emotional Depth

Use poses for deeper emotional responses:

```
@npc-react widow=hello/emote looks at you with sad eyes
@npc-react widow=hello/pose sits quietly, lost in thought
@npc-react widow=love/pose clutches something close to heart
@npc-react widow=miss/emote wipes away a tear
```

### Context-Appropriate Responses

Tailor reactions to NPC personality:

```
# Rough character
@npc-react rough=please/say Please? Don't waste your manners on me.

# Polite character  
@npc-react noble=hello/say Good day to you. A pleasure to make acquaintance.

# Tired character
@npc-react tired=busy/emote sighs heavily
```

---

Feel free to mix and match these reactions or use them as inspiration for your own NPCs!
