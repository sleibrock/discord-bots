var Discordie = require('discordie');

//obnoxious array of fishfacts... will most likely be handled by a scraper some time in the future...
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
'Most fish have little salt in them. Sharks, however, have meat as salty as the ocean they live in.',
'Most fish can see in color and use colors to camouflage themselves or defend themselves and their territory. Most fish have the best possible eyesight for their habitat and can most certainly see you peering at them in a fish tank. Some fish can see polarized and ultraviolet light.',
'A fish does not add new scales as it grows, but the scales it has increase in size. In this way, growth rings are formed and the rings reveal the age of a fish.',
'Fish that have thin fins with a split tail indicate that they move very quickly or may need them to cover great distances. On the other had, fish that live among rocks and reefs near the ocean floor have broad lateral fin and large tails.',
'A ship has a heavy keel in the lower part to keep it from capsizing. Fish, on the other hand, have the keel on top. If the paired fins stop functioning to keep the fish balanced, the fish turns over because its heaviest part tends to sink, which happens when it dies.',
'On average, flying fish can glide 160 feet (50m), but have been known to glide as far as 660 feet (200 m). And they can reach heights up to 19 feet (6m).',
'An inflated porcupine fish can reach a diameter of up to 35 inches (90 cm). It puffs up by swallowing water and then storing it in its stomach. The stomach increases in size with more water. If the fish is taken out of water, it can inflate in a similar way by swallowing air.',
'A fish can drown in water. Like humans, fish need oxygen, so if there isn’t enough oxygen in the water, they will suffocate.',
'The fish in the middle of a school control the school. The fish on the outside are guided by those in the middle. Only bony fish can swim in highly coordinated groups.',
'Most fish cannot swim backwards. Those that can are mainly members of one of the eel families.',
'Fish would suffocate if they tried to chew because chewing would interfere with water passing over their gills.',
'The biggest fish in the world is the giant whale shark, which can grow to nearly 60 feet, or the length of two school buses. It weighs over 25 tons and eats mainly plankton. It has over 4,000 teeth, though they are only 3 mm long.',
'The most poisonous fish in the world is the stone fish. Its sting can cause shock, paralysis, and even death if not treated within a few hours.',
'The word “piranha” is from the Tupi (Brazil) pira nya and means “scissors.” Found in freshwater rivers in South America, piranhas have razor-sharp teeth. They typically eat fish, insects, seeds, fruit, and even larger animals such as horses. While there are no proven reports of piranhas killing a person, they do eat human carcasses.',
'The fastest fish is the sailfish. It can swim as fast as a car travels on the highway.',
'The slowest fish is a seahorse. It swims so slowly that a person can barely tell it is moving. The slowest is the Dwarf Seahorse, which takes about one hour to travel five feet. It even looks like it is simply standing up, not swimming.',
'Some fish do not have scales. Sharks, for example, have rough sandpapery skin instead of scales.',
'Fish have multiple Christian and pre-Christian overtones. For example, the Greek word for fish is Ichthys, which is an acronym for "Jesus Christ, God’s Son, Savior" and was used to mark early Christian tombs and meeting places. Because of their association with fertility, fish have also been linked to Isis and Aphrodite.',
'In Japan, the fugu, or puffer fish, is a succulent but lethal delicacy. It contains tetrodotoxin, a deadly poison. However, it is so delicious that Japanese gourmets risk their lives to prepare it. To make this high-risk dish, chefs must have a certificate from a special school that teaches preparation of this toxic fish.',	
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
	//generate a fish fact based on a user message using ! as a delimiter to indicate that the bot should respond
	var incoming = e.message.content.toLowerCase();

	if(incoming == '!fishfact')
	{
		//generate a random fishfact from the fishfact array and send to the channel as a message
		var random = Math.floor(Math.random()*factArray.length);
		var message = 'Fish Fact #' + (random +1) + "  - " +  factArray[random];
		e.message.channel.sendMessage(message);
	}

	if(incoming.startsWith('!') && incoming.endsWith('fact') && incoming !== '!fishfact')
	{
		//generate a fish fact based on the type of fish requested by the user
		var fish = incoming.substring(1,incoming.length-4);
		var fishArray = [];
		//create a new array to hold the info about the fish
		for(var i = 0; i < factArray.length; i++)
		{
			if(factArray[i].includes(fish))
			{
				fishArray.push(factArray[i]);
			}
		}
		// if theres no info about th desired fish let the user know nothing was found
		if(fishArray.length == 0)
		{
			e.message.channel.sendMessage('I dont know anything about that!');
		}

		else
		{
			//otherwise send a random fact about the desired fish
			fish = fish.charAt(0).toUpperCase() + fish.slice(1);
			var random = Math.floor(Math.random()*fishArray.length);
			var message = fish + ' Fact #' + (random +1) + ' - ' + fishArray[random];
			e.message.channel.sendMessage(message);
		}
	}
	if(incoming.includes('!fishfact#'))
	{
		//generate a specific fish fact for the user based on the total (currently 40)
		var whichFact = incoming.substring(10,incoming.lenth);
		var factNum = parseInt(whichFact);
		//send a message letting the user know they messed up the input either by putting in a negative number, non number, or a number that is too large
		if(factNum > factArray.length)
		{
			e.message.channel.sendMessage("I don't know that many facts yet! I only know " + factArray.length + ' facts.');
		}
		else if(factNum == NaN)
		{
			e.message.channel.sendMessage("Your fact number was either negative or not a number... Don't try and fool me!");
		}
		else
		{
			//if the input is ok send the desired fact back!
			var random = Math.floor(Math.random()*factArray.length);
			var message = 'Fish Fact #' + factNum + "  - " +  factArray[factNum-1];
			e.message.channel.sendMessage(message);
		}
	}
});


