"""
Screenplay for the animated adaptation of
THE BOY WHO WANTED TO FLY — Story by Jason Whitewolf (© 2018, all rights reserved).

The canonical text lives untouched in /manuscript. This file is the production
adaptation: the narration follows the manuscript closely, quoted speech is
voiced by characters, and a few lines are lightly trimmed for pacing.
Every adaptation choice is listed in docs/ADAPTATION_NOTES.md.

Speakers: N narrator, O Orion, M Mom, D Dad, G garbage-truck driver.
Each beat may carry a `tag` that the scene animation uses as a cue.
`pause` is extra silence (seconds) after the line.
"""

SCENES = [
 # ---------------------------------------------------------------- SCENE 1
 {"id": 1, "title": "A Big Dream", "beats": [
  ("N", "Orion was a young boy with a big dream: to learn how to fly.", "intro", 0.6),
  ("N", "Ever since he was very little, he had dreamed of soaring through the sky, and this autumn was no exception.", "dream", 0.5),
  ("N", "One Saturday, Orion had a thought.", "thought", 0.2),
  ("O", "If I'm going to fly, I need to make some wings!", "idea", 0.5),
  ("N", "So he went to the garage and searched for materials. He found some empty cardboard boxes, and grabbed a pair of scissors and some tape from the workbench.", "garage", 0.4),
  ("N", "He spent a long time in the garage, cutting and shaping the cardboard into wing shapes. He used the tape to secure the wings to his arms, making sure they wouldn't fall off.", "build", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 2
 {"id": 2, "title": "Flap, Flap, Flap", "beats": [
  ("N", "Finally, his wings were ready. He walked out to the front yard, put on his wings, and started running around, flapping his arms as hard as he could.", "run", 0.3),
  ("N", "But no matter how fast he ran, or how high he jumped, he couldn't get off the ground. He flapped his arms as hard as he could, and ran as fast as he could, but he still could not fly.", "fail", 0.4),
  ("N", "After a long time running around his front yard, Orion got tired, and sat down on the grass to rest.", "rest", 0.5),
  ("N", "The golden sun was slowly starting to set, as it gently dipped below the horizon. The leaves on the trees rustled in the cool autumn breeze.", "sunset", 0.3),
  ("N", "The crisp air was filled with the scent of falling leaves, wood smoke, and the sweet aroma of ripe apples and pumpkins.", "scent", 0.3),
  ("M", "Orion! Dinner time!", "call", 0.3),
  ("N", "He took off his wings and put them in the garage, then went inside to eat his favorite meal: spaghetti with meatballs.", "dinner", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 3
 {"id": 3, "title": "A Room Full of Flying Things", "beats": [
  ("N", "After dinner, Orion helped his mom and dad clean up and wash the dishes.", "dishes", 0.3),
  ("N", "Then he headed up to his bedroom to get ready for bed. His bedroom was his own personal retreat, a place where he could relax and be himself.", "stairs", 0.4),
  ("N", "His walls were covered in pictures of airplanes, birds, and superheroes, all of them flying through the air. Orion spent a few moments gazing at them, imagining what it would be like to fly.", "walls", 0.5),
  ("N", "After changing into his pajamas and brushing his teeth, he climbed into bed and snuggled under the covers.", "bed", 0.3),
  ("N", "He felt grateful for his warm, comfortable bed, and the roof over his head. He fell asleep with a smile on his face.", "sleep", 1.0),
 ]},
 # ---------------------------------------------------------------- SCENE 4
 {"id": 4, "title": "Blueberry Pancakes", "beats": [
  ("N", "The next morning, Orion woke up with a new idea.", "wake", 0.2),
  ("O", "What if I put feathers on my cardboard wings?", "idea", 0.3),
  ("N", "He was so excited that he jumped out of bed, got dressed quickly, and started running down the stairs.", "run", 0.1),
  ("O", "This just might work!", "run2", 0.2),
  ("M", "No running down the stairs!", "mom", 0.2),
  ("N", "This wasn't the first time she had reminded him of this rule.", "rule", 0.2),
  ("O", "Yes, Mom.", "yes", 0.3),
  ("M", "Eat your blueberry pancakes before you go out to play.", "pancakes", 0.2),
  ("O", "Oh, man.", "groan", 0.3),
  ("N", "He really just wanted to try out his new idea. But he eagerly finished his breakfast, and asked if he could go outside to play.", "eat", 0.2),
  ("M", "Of course you can.", "yes2", 0.3),
  ("N", "He leapt from the table with so much excitement that he almost knocked over his chair. He quietly put it back in place, and hurried out to the garage to get his cardboard wings.", "leap", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 5
 {"id": 5, "title": "Feathers from the Coop", "beats": [
  ("N", "He gathered feathers from the chicken coop, trying his best not to disturb the chickens, who were busy clucking and pecking about.", "coop", 0.3),
  ("N", "As he searched for the perfect feathers, he couldn't help but laugh at the silly birds. One particularly mischievous chicken kept trying to sneak up and peck at his shoes.", "peck", 0.4),
  ("N", "Orion gathered a good supply of feathers, and taped them to his homemade wings. He was so excited to test them out that he barely noticed the chicken that was now tugging at the hem of his shirt.", "tape", 0.3),
  ("O", "This should work!", "work", 0.3),
  ("N", "He put on his feathery wings and ran out to the front yard.", "out", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 6
 {"id": 6, "title": "Here Goes Nothing", "beats": [
  ("O", "Here goes nothing!", "go", 0.2),
  ("N", "Orion took off running at top speed, flapping his arms as hard as he could. At first, he struggled to get off the ground, but he refused to give up. He kept running and flapping, panting and sweating as he ran.", "run", 0.4),
  ("N", "Eventually, he got tired and collapsed onto the grass, feeling a mix of frustration and determination. He couldn't help but wonder what he was doing wrong.", "collapse", 0.3),
  ("N", "Then, a sudden spark of inspiration hit him.", "spark", 0.1),
  ("O", "Maybe I just need to jump higher!", "idea", 0.3),
  ("N", "He ran back to the garage, rummaged through the clutter until he found a ladder and a rake, and hurried back to the front yard.", "ladder", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 7
 {"id": 7, "title": "The Leaf Pile", "beats": [
  ("N", "It was late autumn, and the trees in Orion's yard were ablaze with color. Red, orange, pink, yellow, and brown. Most of the leaves had already fallen, creating a carpet of color across the lawn.", "trees", 0.4),
  ("N", "He raked the leaves together into a large and fluffy heap, and placed the tall ladder right next to it.", "rake", 0.3),
  ("N", "He climbed to the very top, started flapping his new wings, and then, with all his might, he jumped!", "jump", 0.3),
  ("N", "Orion didn't fly at all. Instead, he fell right into the big pile of leaves, sending them flying up into the air around him.", "splash", 0.3),
  ("N", "Even though he couldn't fly, it was still a lot of fun. So, laughing and tumbling, he tried it again, and again.", "again", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 8
 {"id": 8, "title": "The Garbage Truck Driver", "beats": [
  ("N", "A short time later, a garbage truck came rumbling down the street, and stopped in front of his house.", "truck", 0.3),
  ("N", "The driver, a tall and burly man with a rough, stubbly face and large shoes, walked towards Orion. Despite his appearance, Orion could see kindness in the man's eyes as he knelt down to speak to him.", "kneel", 0.3),
  ("G", "Do you really want to learn to fly?", "ask", 0.3),
  ("O", "More than anything.", "reply", 0.4),
  ("N", "The man chuckled.", "chuckle", 0.1),
  ("G", "If you really want to fly, then you can fly in your dreams.", "dreams", 0.3),
  ("O", "How do I do that?", "how", 0.3),
  ("G", "Practice, my boy. Practice. Just keep practicing, and never give up on your dream.", "practice", 0.4),
  ("N", "With a smile and a wave, the man returned to his truck and drove away.", "leave", 0.3),
  ("N", "Orion lay in the leaves, gazing up at the sky, and made a promise to himself: to never give up on his dream of flying, and to practice every chance he got.", "promise", 1.0),
 ]},
 # ---------------------------------------------------------------- SCENE 9
 {"id": 9, "title": "Goodnight", "beats": [
  ("N", "That night, Orion climbed into his cozy bed in the corner of his room. The blankets were soft and thick, and always made him feel warm and secure.", "bed", 0.3),
  ("N", "He wondered if he would be able to fly in his dreams.", "wonder", 0.3),
  ("N", "A short while later, his parents came into his room. His mother leaned down to kiss him on the forehead, her long hair tickling his face.", "parents", 0.3),
  ("O", "Hey Dad, do you think I can fly in my dreams?", "ask", 0.4),
  ("D", "I think you can.", "dad", 0.4),
  ("N", "This made him very happy. He snuggled deeper into his blankets, already feeling the weightless sensation of flight in his mind. He let out a contented sigh, and before he knew it, he had drifted off into a deep and peaceful sleep.", "sleep", 1.2),
 ]},
 # ---------------------------------------------------------------- SCENE 10
 {"id": 10, "title": "Running Through Honey", "beats": [
  ("N", "He could hear the howling wind outside, and the tapping of a branch on his window. Tap. Tap. Tap.", "tap", 0.6),
  ("N", "The noise almost woke him up, but he did not want to wake up, because he was having a really good dream. Then he remembered: he should try to fly in his dreams!", "remember", 0.3),
  ("N", "So in his dream, he started flapping his arms and tried to run super fast. But it felt like he was running through honey.", "honey", 0.3),
  ("N", "The thick, sticky honey slowed every step. His feet felt stuck to the ground, his legs heavy and sluggish.", "stuck", 0.4),
  ("N", "Frustrated, he dreamed instead about his friends, and the swimming pool they used to visit every summer. The sound of laughter and splashing as they played and swam. That was a very nice dream.", "pool", 1.0),
 ]},
 # ---------------------------------------------------------------- SCENE 11
 {"id": 11, "title": "The Cape", "beats": [
  ("N", "The next morning, Orion's mind was still racing from the night's dream. It had been so hard to run that he could not even jump!", "morning", 0.3),
  ("N", "He could vividly recall every detail, from the cool night air, to the way his heart seemed to pulse with the power of flight.", "recall", 0.3),
  ("N", "He thought about this for a while, until he got a new idea.", "think", 0.2),
  ("O", "Maybe if I wear my Superman cape, it will help me fly in my sleep!", "cape", 0.4),
  ("N", "So that night, before he went to bed, he put on his cape. And then, he fell asleep.", "sleep", 1.0),
 ]},
 # ---------------------------------------------------------------- SCENE 12
 {"id": 12, "title": "Like a Bubble", "beats": [
  ("N", "A few hours later, Orion found himself back in the dream world, determined to fly. He knew that this was his chance.", "dreamworld", 0.3),
  ("N", "This time, he had on his cape. It was made of a shiny red fabric that flowed behind him as he moved. It always made him feel like a superhero, ready to take on any challenge.", "cape", 0.3),
  ("N", "He really believed he could do it this time. So, in his dream, he jumped into the air as hard as he could!", "jump", 0.4),
  ("N", "Then, a very amazing thing happened. He started to fly!", "fly", 0.5),
  ("N", "He was floating in the air, like a bubble. But when he tried to control his flying, he once again had a hard time.", "bubble", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 13
 {"id": 13, "title": "Hands and Thumbs", "beats": [
  ("N", "Orion spread his arms out in front of him, just like Superman, and for a moment, it seemed to work.", "arms", 0.2),
  ("O", "Maybe Superman flies with his hands?", "hands", 0.3),
  ("N", "But flying with his hands was a lot harder than he expected. His movements felt wobbly and uncertain, like balancing on a tightrope.", "wobble", 0.3),
  ("O", "Maybe Superman flies with his thumbs?", "thumbs", 0.3),
  ("N", "That was even more difficult! Every time he moved his thumbs, even just a little bit, his body would zip sharply in that direction.", "zip", 0.3),
  ("O", "Well, that's not going to work!", "nope", 0.3),
  ("N", "Flying in his dreams was a lot harder than he had imagined. But even so, he wasn't ready to give up just yet.", "persist", 0.8),
 ]},
 # ---------------------------------------------------------------- SCENE 14
 {"id": 14, "title": "The Heart", "beats": [
  ("O", "Maybe Superman can fly so well because of the letter S on his chest!", "chest", 0.3),
  ("N", "So Orion stuck out his chest and began to fly. And amazingly, something was very different this time. He could control his flying!", "control", 0.3),
  ("N", "The further he pushed out his chest, the faster he would fly. When he pulled his chest back, he could easily slow down. And when he moved his chest to the left and the right, he would fly that way too!", "steer", 0.5),
  ("N", "But then, Orion thought to himself:", "thought", 0.1),
  ("O", "I don't have an S on my chest. So how can I do it?", "nos", 0.6),
  ("O", "Maybe... it's my heart that makes me fly!", "heart", 1.4),
 ]},
 # ---------------------------------------------------------------- SCENE 15
 {"id": 15, "title": "Over the Moon", "beats": [
  ("N", "Orion's heart was so full of love for flying, that it made his heart very powerful. So he opened his heart all the way, as much as he could, and let all his love for flying guide him.", "open", 0.4),
  ("N", "He flew higher and higher, laughing with joy as the wind rushed past him. It was the most amazing feeling he had ever experienced.", "higher", 0.4),
  ("N", "He flew all around the neighborhood. Over houses, and trees.", "neighborhood", 0.3),
  ("N", "Through the clouds.", "clouds", 0.4),
  ("N", "And over the moon!", "moon", 0.6),
  ("N", "He flew higher and higher, until he was soaring through the starry sky. It was the most incredible adventure of his life.", "stars", 0.4),
  ("N", "Then he began to fly faster, and faster, and faster!", "faster", 1.0),
 ]},
 # ---------------------------------------------------------------- SCENE 16
 {"id": 16, "title": "Shoes on the Wire", "beats": [
  ("N", "Orion flew so incredibly fast in his dreams that night, that he lost his shoes!", "lost", 0.4),
  ("N", "His shoes came right off his feet, because his shoelaces were not tied on tight enough.", "laces", 0.6),
  ("N", "And that is why, if you ever see a pair of shoes hanging from a telephone wire...", "wire", 0.4),
  ("N", "they were lost by kids who were flying in their dreams.", "reveal", 2.0),
 ]},
 # ---------------------------------------------------------------- SCENE 17
 {"id": 17, "title": "The Boy Who Could Fly", "beats": [
  ("N", "From that day on, Orion was known as the boy who could fly.", "known", 0.4),
  ("N", "He flew in his dreams all the time, exploring the world, and having adventures.", "adventures", 0.4),
  ("N", "And every time he flew, he remembered the long journey it had taken him to get there.", "journey", 0.4),
  ("N", "But it was all worth it, because he had finally achieved his dream of learning how to fly.", "worth", 1.0),
  ("N", "The end.", "end", 2.5),
 ]},
]

# Voice casting (Kokoro v1.0 voices, Apache-2.0). pitch = playback-rate shift
# applied after synthesis (1.0 = none); >1 raises pitch (younger), <1 deepens.
VOICES = {
 "N": {"voice": "af_heart",   "speed": 0.90, "pitch": 1.00},
 "O": {"voice": "af_sky:0.65,af_bella:0.35", "speed": 1.00, "pitch": 1.16},
 "M": {"voice": "af_bella",   "speed": 0.95, "pitch": 1.00},
 "D": {"voice": "am_michael", "speed": 0.90, "pitch": 0.98},
 "G": {"voice": "am_fenrir",  "speed": 0.86, "pitch": 0.90},
}
