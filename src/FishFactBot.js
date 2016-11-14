var Discordie = require('discordie');


var factArray = 
[
'Most fish reproduce by laying eggs, though some fish, such as great white sharks, give birth to live babies called pups.',
'Starfish are not fish. Neither are jellyfish.',
"Although the fangtooth fish is only a few inches long, it has teeth about the size of a human's.",
'The mudskipper is a fish that spends most of its time out of water and can "walk" on its fins. It carries a portable water supply in its gill chambers when it leaves the water. It can also breathe through the pores of its wet skin.',
'Catfish have over 27,000 taste buds. Humans have around 7,000.',
'Most brands of lipstick contain fish scales.',
'Lungfish can live out of water for several years. It secretes a mucus cocoon and burrows itself under the unbaked earth. It takes in air with its lung through a built-in breathing tube that leads to the surface. A lungfish has both gills and a lung.',
'Seahorses are the only fish that swim upright.',
'Some fish, such as the great white shark, can raise their body temperature. This helps them hunt for prey in cold water.',
'The oldest known age for a fish was an Australian lungfish. In 2003, it was still alive and well at 65 years old.',
'Fish use a variety of low-pitched sounds to convey messages to each other. They moan, grunt, croak, boom, hiss, whistle, creak, shriek, and wail. They rattle their bones and gnash their teeth. However, fish do not have vocal chords. They use other parts of their bodies to make noises, such as vibrating muscles against their swim bladder.',
'Fish can form schools containing millions of fish. They use their eyes and something called a lateral line to hold their places in the school. The lateral line is a row of pores running along the fish’s sides from head to tail. Special hairs in the pores sense changes in water pressure from the movements of other fish or predators.',
'Since a fish’s jaw is not attached to its skull, many fishes can shoot their mouths forward like a spring to catch startled prey.',
'Electric eels and electric rays have enough electricity to kill a horse',
'Sharks are the only fish that have eyelids.',
'Fish have sleep-like periods where they have lowered response to stimuli, slowed physical activity, and reduced metabolism but they do not share the same changes in brain waves as humans do when they sleep.',
'Some fish, such as the herbivorous fish (grazers), often lack jaw teeth but have tooth-like grinding mills in their throats called pharyngeal teeth.',
'Most fish have taste buds all over their body.',
'An estimated one third of male fish in British waters are changing sex due to pollution in human sewage.',
'Saltwater fish need to drink more water than freshwater fish. Since seawater is saltier than the liquids in a fish’s body, water inside the fish is constantly flowing out. If they didn’t drink to replace the lost water, saltwater fish would dry up like prunes.',
'The oldest fishhook ever found dates back to about 42,000 years ago.',
];


const Events = Discordie.Events;
const client = new Discordie();


client.connect(
{
	token: 'MjQ2NTczMzYxOTIzMDk2NTc2.Cwcm5A.d2e1XhYxTnwErVkHIn33OzuptOE'
})


client.Dispatcher.on(Events.GATEWAY_READY, e => {
	console.log('Connected as: FISHFACTBOT5000');
});

client.Dispatcher.on(Events.MESSAGE_CREATE, e => {
	if(e.message.content.toLowerCase() == '!fishfact')
	{
		var random = Math.floor(Math.random()*factArray.length);
		var message = 'Fish Fact #' + (random +1) + "  - " +  factArray[random];
		e.message.channel.sendMessage(message);
	}
});


