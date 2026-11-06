"""Version 3 shot list: one key image per shot, generated with Z-Image Turbo.

Characters and places are described the same way in every prompt so they stay
consistent without a trained LoRA. `beats` lists the screenplay beat tags
(script/screenplay.py) a shot covers; `p` is the generation priority:
1 = needed for the first complete cut, 2 = enrichment pass.
"""

STYLE = ("modern 3D animated feature film style, soft stylized appealing proportions, subsurface "
         "scattering skin, expressive eyes, rich cinematic lighting, detailed textures, high detail")
DREAM = "dreamlike magical atmosphere, soft glowing light, luminous colors"

ORION = ("Orion, a 7-year-old boy with messy chestnut-brown hair and a cowlick, big expressive hazel eyes, "
         "light freckles, round friendly face")
DAY_CLOTHES = "wearing a long-sleeve shirt with horizontal orange and cream stripes, blue jeans and red canvas sneakers"
PAJAMAS = "wearing light-blue and white striped flannel pajamas"
CAPE = "and a plain shiny red cape with no logo"
WINGS = "homemade cardboard wings taped onto both of his arms"
FEATHER_WINGS = "homemade cardboard wings covered in white and brown chicken feathers, taped onto both of his arms"
MOM = ("his mom, a warm woman in her thirties with long wavy chestnut-brown hair, wearing a soft sage-green "
       "cardigan over a cream top")
DAD = ("his dad, a kind man in his late thirties with short dark-brown hair, a short trimmed beard and "
       "glasses, wearing a blue and green plaid flannel shirt")
DRIVER = ("a tall burly garbage truck driver with a rough stubbly face and kind gentle eyes, wearing an orange "
          "high-visibility vest over a grey work shirt, work gloves and very large boots")
HOUSE = ("a cozy two-story pale-yellow house with white trim, a front porch and a red front door, big maple "
         "trees with red and orange leaves in the front yard, a wooden telephone pole and wires along the street")
YARD = "the front lawn of " + HOUSE + ", fallen red, orange and yellow maple leaves on the grass"


def P(text, dream=False):
    return f"Film still, {STYLE}{', ' + DREAM if dream else ''}. {text}"


SHOTS = [
    # ---- 1  A Big Dream
    dict(id="s01a", p=1, beats=["intro", "dream"], prompt=P(
        f"Wide establishing shot of a peaceful autumn suburban street on a crisp sunny morning: {HOUSE}. "
        "A flock of birds flies across the blue sky above the rooftops, gentle golden light.")),
    dict(id="s01b", p=2, beats=["dream"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, lies on his back on the autumn lawn with his arms spread like wings, "
        "smiling up at a flock of birds flying high overhead in a clear blue sky, leaves around him.")),
    dict(id="s01c", p=1, beats=["thought", "idea", "garage"], prompt=P(
        f"Inside a cluttered warm family garage with a workbench, tools on a pegboard and dusty sunbeams from "
        f"a small window: {ORION}, {DAY_CLOTHES}, holds up a flattened cardboard box with a bright excited "
        "idea on his face, a roll of tape and scissors on the workbench.")),
    dict(id="s01d", p=2, beats=["build"], prompt=P(
        "Close-up of a small boy's hands carefully cutting a big wing shape out of cardboard with scissors on a "
        "wooden workbench, pencil lines, scraps of cardboard and a roll of tape, warm sunbeam, shallow depth of field.")),
    dict(id="s01e", p=1, beats=["build"], prompt=P(
        f"In a warm cluttered garage, {ORION}, {DAY_CLOTHES}, proudly holds his arms out wide to show off "
        f"{WINGS}, beaming with pride, sunlight streaming through the open garage door behind him.")),
    # ---- 2  Flap, Flap, Flap
    dict(id="s02a", p=1, beats=["run"], reuse="v3/review/A3_hero_run_s1.png"),
    dict(id="s02b", p=2, beats=["fail"], prompt=P(
        f"{ORION}, {DAY_CLOTHES} and {WINGS}, jumps as high as he can on {YARD}, flapping hard, eyes squeezed "
        "shut with effort, a few leaves kicked up, golden afternoon light, funny and charming.")),
    dict(id="s02c", p=1, beats=["rest", "sunset"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, sits tired on the autumn grass with his cardboard wings lying beside him, "
        "watching the golden sun set low on the horizon, his face lit warm gold, a V-shaped flock of geese "
        "crossing the orange sky, peaceful and a little wistful.")),
    dict(id="s02d", p=2, beats=["scent"], prompt=P(
        "Wide golden-hour view over autumn rooftops of a cozy neighborhood at sunset, wisps of wood smoke from "
        "a chimney, maple leaves drifting in the breeze, pumpkins and a basket of red apples on a porch.")),
    dict(id="s02e", p=1, beats=["call"], prompt=P(
        f"At sunset, {MOM} stands alone in the open red front door of {HOUSE}, warm light glowing from "
        "inside, cupping one hand beside her mouth and calling out across the empty front yard, smiling. "
        "She is the only person in the picture.")),
    dict(id="s02f", p=1, beats=["dinner"], prompt=P(
        f"A cozy family kitchen table in the evening, warm lamp light: {ORION}, {DAY_CLOTHES}, happily twirls a "
        f"forkful of spaghetti from a big plate of spaghetti and meatballs, {MOM} and {DAD} smiling at him.")),
    # ---- 3  A Room Full of Flying Things
    dict(id="s03a", p=1, beats=["dishes"], prompt=P(
        f"In a warm family kitchen at night, {ORION}, {DAY_CLOTHES}, stands on a step stool at the sink drying a plate with a "
        f"towel, {MOM} washing dishes with soap bubbles and {DAD} putting plates away, all laughing together.")),
    dict(id="s03b", p=2, beats=["stairs"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, climbs a carpeted staircase in a cozy house at night with a hopeful smile, "
        "family photos on the wall, warm hallway light above.")),
    dict(id="s03c", p=1, beats=["stairs", "walls"], prompt=P(
        f"A cozy child's bedroom at night lit by a warm lamp, the walls covered in posters and drawings of "
        "airplanes, birds, hot-air balloons and a caped kid hero with a star on his chest, a model airplane "
        f"hanging from the ceiling: {ORION}, {DAY_CLOTHES}, stands gazing up at them in wonder.")),
    dict(id="s03d", p=2, beats=["bed"], prompt=P(
        f"{ORION}, {PAJAMAS}, brushes his teeth at a small bathroom sink, standing on a step stool, foam on his "
        "lips, sleepy and cute, warm night lighting.")),
    dict(id="s03e", p=1, beats=["bed", "sleep"], prompt=P(
        f"{ORION}, {PAJAMAS}, sleeps snuggled under a thick soft quilt in a cozy bed in the corner of his "
        "bedroom, a peaceful smile on his face, soft blue moonlight from the window, posters of airplanes and "
        "birds on the walls.")),
    # ---- 4  Blueberry Pancakes
    dict(id="s04a", p=1, beats=["wake", "idea"], prompt=P(
        f"Bright morning sunlight floods a cozy bedroom: {ORION}, {PAJAMAS}, sits bolt upright in bed with wide "
        "excited eyes and a huge grin, struck by a brilliant idea, hair sticking up from sleep.")),
    dict(id="s04b", p=2, beats=["run", "run2"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, bounds eagerly down a wooden staircase in a sunny house in the morning, "
        "mid-step, motion and excitement, hair flying.")),
    dict(id="s04c", p=1, beats=["mom", "rule", "yes"], prompt=P(
        f"Sunny morning kitchen: {MOM} holds a spatula at the stove and gives a knowing look with a raised "
        f"eyebrow and a smile toward the stairs, where {ORION}, {DAY_CLOTHES}, has frozen mid-step on the "
        "bottom stairs with a sheepish grin.")),
    dict(id="s04d", p=1, beats=["pancakes", "groan", "eat", "yes2"], prompt=P(
        f"Morning kitchen table: {ORION}, {DAY_CLOTHES}, sits in front of a tall stack of blueberry pancakes "
        "with syrup and butter, cheeks puffed, eating fast and impatient, glancing at the back door, sunlight "
        "through the window.")),
    dict(id="s04e", p=2, beats=["leap"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, leaps up from the kitchen table so excited that his wooden chair tips "
        "backward behind him, a funny moment, bright morning kitchen.")),
    # ---- 5  Feathers from the Coop
    dict(id="s05a", p=1, beats=["coop", "silly"], prompt=P(
        f"A rustic backyard chicken coop with straw and a little wooden henhouse in dappled morning sunlight: "
        f"{ORION}, {DAY_CLOTHES}, tiptoes among clucking brown and white chickens, picking up a feather and "
        "laughing.")),
    dict(id="s05b", p=2, beats=["peck"], prompt=P(
        "Low angle close-up in a chicken coop: a mischievous fluffy brown hen with a cheeky expression pecks "
        "at the toe of a small red canvas sneaker, straw and feathers around, comedic.")),
    dict(id="s05c", p=1, beats=["tape", "work"], prompt=P(
        f"On the back porch steps, {ORION}, {DAY_CLOTHES}, happily tapes white and brown chicken feathers onto "
        "his cardboard wings, totally focused, while a cheeky brown hen behind him tugs at the hem of his "
        "shirt with her beak, morning light, funny.")),
    # ---- 6  Here Goes Nothing
    dict(id="s06a", p=1, beats=["go", "run"], prompt=P(
        f"{ORION}, {DAY_CLOTHES} and {FEATHER_WINGS}, sprints across {YARD} at top speed, flapping with fierce "
        "determination, feathers fluttering off behind him, dynamic low angle, bright midday sun.")),
    dict(id="s06b", p=1, beats=["collapse", "idea"], prompt=P(
        f"{ORION}, {DAY_CLOTHES} and {FEATHER_WINGS}, sits flopped on the autumn lawn, sweaty and out of "
        "breath, then gets a sudden bright idea, eyes lighting up, finger raised, midday light.")),
    dict(id="s06c", p=2, beats=["ladder"], prompt=P(
        f"In a cluttered garage, {ORION}, {DAY_CLOTHES}, drags out a tall aluminium ladder and a leaf rake "
        "from behind boxes and bicycles, determined and excited.")),
    # ---- 7  The Leaf Pile
    dict(id="s07a", p=1, beats=["autumn", "colors"], prompt=P(
        f"Wide shot of {YARD} in late autumn, the maple trees ablaze with red, orange, pink, yellow and brown "
        "leaves, a thick carpet of fallen leaves across the lawn, warm afternoon sun, leaves drifting down.")),
    dict(id="s07b", p=2, beats=["rake"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, rakes fallen maple leaves into a huge fluffy colorful pile on the front lawn, "
        "proud and happy, afternoon light.")),
    dict(id="s07c", p=1, beats=["ladder"], prompt=P(
        f"{ORION}, {DAY_CLOTHES} and {FEATHER_WINGS}, stands carefully at the top of a tall ladder next to an "
        "enormous fluffy pile of red and orange leaves on the lawn, arms spread wide, bravely getting ready to "
        "jump, low angle against a blue autumn sky.")),
    dict(id="s07d", p=1, beats=["jump", "again"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, crashes laughing into a huge fluffy pile of autumn leaves, red, orange and "
        "yellow leaves exploding into the air all around him, pure joy, golden afternoon light.")),
    # ---- 8  The Garbage Truck Driver
    dict(id="s08a", p=1, beats=["truck"], prompt=P(
        f"A friendly green garbage truck rumbles down a leafy autumn street and stops in front of {HOUSE}, "
        "leaves swirling behind it, late afternoon golden light.")),
    dict(id="s08b", p=2, beats=["driver"], prompt=P(
        f"Low angle: {DRIVER} climbs down from the cab of a green garbage truck on an autumn street, his huge "
        "boots landing in the fallen leaves.")),
    dict(id="s08c", p=1, beats=["kneel", "ask", "reply", "dreams", "how"], prompt=P(
        f"On a leaf-covered lawn in golden afternoon light, {DRIVER} kneels down to talk gently with {ORION}, "
        f"{DAY_CLOTHES}, who sits in a pile of leaves looking up at him with wide hopeful eyes, a green garbage "
        "truck parked on the street behind them.")),
    dict(id="s08d", p=2, beats=["practice", "never"], prompt=P(
        f"Close-up of {DRIVER} smiling warmly with crinkled kind eyes, giving a thumbs-up, golden autumn light.")),
    dict(id="s08e", p=1, beats=["leave", "ponder", "promise"], prompt=P(
        f"{ORION}, {DAY_CLOTHES}, lies on his back in a big pile of autumn leaves gazing thoughtfully up at "
        "the sky with a quiet determined smile, a green garbage truck driving away down the street in the "
        "distance, soft late-afternoon light.")),
    # ---- 9  Goodnight
    dict(id="s09a", p=1, beats=["bed", "wonder"], prompt=P(
        f"{ORION}, {PAJAMAS}, lies in his cozy bed in the corner of his bedroom at night with a thick plush "
        "quilt pulled up to his chin, eyes open, wondering, soft lamp light and moonlight from the window.")),
    dict(id="s09b", p=1, beats=["kiss", "ask", "dad"], prompt=P(
        f"A cozy child's bedroom at night: {MOM} leans down to kiss {ORION} on the forehead as he lies in bed "
        f"{PAJAMAS}, her long hair falling near his face, while {DAD} stands beside the bed smiling warmly, "
        "soft warm lamp light.")),
    dict(id="s09c", p=2, beats=["sleep"], prompt=P(
        f"Close-up of {ORION}, {PAJAMAS}, asleep in bed, snuggled deep in a plush quilt, a content smile on his face, "
        "soft silver moonlight, peaceful.", dream=True)),
    # ---- 10  Running Through Honey
    dict(id="s10a", p=1, beats=["wind", "tap"], prompt=P(
        "Night, windy: a bare twisting maple branch taps against a child's bedroom window, autumn leaves "
        "whirling past in the wind, moonlight, the warm glow of a night light inside, moody and magical.")),
    dict(id="s10b", p=1, beats=["dreamrun", "honey"], prompt=P(
        f"A dream: {ORION}, {PAJAMAS}, tries to run through a strange golden landscape flooded with thick "
        "glistening amber honey up to his knees, straining with every slow step, arms flapping, honey "
        "stretching from his legs, warm golden glow.", dream=True)),
    dict(id="s10c", p=1, beats=["pool"], prompt=P(
        f"A warm hazy summer memory: {ORION} and his friends laugh and splash in a sparkling blue neighborhood "
        "swimming pool on a sunny day, water droplets glittering in the sunlight, joyful.", dream=True)),
    # ---- 11  The Cape
    dict(id="s11a", p=1, beats=["morning", "remember", "idea"], prompt=P(
        f"Morning in a cozy bedroom: {ORION}, {PAJAMAS}, lies in bed with his hands behind his head, staring "
        "at the ceiling deep in thought, then a smile of a new idea, soft morning sunlight.")),
    dict(id="s11b", p=1, beats=["cape"], prompt=P(
        f"Night in his bedroom: {ORION}, {PAJAMAS} {CAPE} tied around his neck, stands on his bed in a proud "
        "heroic pose with fists on his hips, the cape flowing, lamp light, determined and adorable.")),
    # ---- 12  Like a Bubble
    dict(id="s12a", p=1, beats=["dreamworld", "jump"], prompt=P(
        f"A dream world of soft violet and peach clouds: {ORION}, {PAJAMAS} {CAPE}, crouches and jumps as hard "
        "as he can, determined, the cape flowing behind him.", dream=True)),
    dict(id="s12b", p=1, beats=["float", "control"], prompt=P(
        f"In a dreamy violet and peach sky, {ORION}, {PAJAMAS} {CAPE}, floats in the air like a bubble, "
        "amazed and delighted, arms flailing a little as he wobbles, cape drifting.", dream=True)),
    # ---- 13  Hands and Thumbs
    dict(id="s13a", p=1, beats=["hands", "hope", "focus"], prompt=P(
        f"In a dreamy sky above soft clouds, {ORION}, {PAJAMAS} {CAPE}, flies with both arms stretched out in "
        "front of him like a superhero, wobbling uncertainly, concentrating hard.", dream=True)),
    dict(id="s13b", p=1, beats=["thumbs", "zip", "nope"], prompt=P(
        f"In a dreamy sky, {ORION}, {PAJAMAS} {CAPE}, zips sharply sideways with both thumbs stuck out, a "
        "surprised comical expression, swooshing motion trails behind him, funny.", dream=True)),
    # ---- 14  The Heart
    dict(id="s14a", p=1, beats=["chest", "control"], prompt=P(
        f"{ORION}, {PAJAMAS} {CAPE}, flies smoothly and confidently through a glowing dream sky with his chest "
        "pushed out proudly, banking gracefully in a turn, a big joyful grin, warm sunrise colors.", dream=True)),
    dict(id="s14b", p=1, beats=["noS", "heart"], prompt=P(
        f"Close-up of {ORION}, {PAJAMAS} {CAPE}, floating in a twilight dream sky with a hand on his chest, "
        "a warm soft golden light glowing from his heart, eyes wide with wonder and realization.", dream=True)),
    # ---- 15  Over the Moon
    dict(id="s15a", p=1, beats=["open", "higher"], prompt=P(
        f"{ORION}, {PAJAMAS} {CAPE}, soars upward with arms wide open and a warm golden glow from his heart, "
        "laughing with joy, wind in his hair, sparkling light trails, magical sky.", dream=True)),
    dict(id="s15b", p=1, beats=["neighborhood"], prompt=P(
        f"Aerial view: {ORION}, {PAJAMAS} {CAPE}, flies joyfully over his autumn neighborhood, the rooftops "
        "and red and orange maple trees far below, warm golden evening light, birds flying alongside him.",
        dream=True)),
    dict(id="s15c", p=1, beats=["clouds"], prompt=P(
        f"{ORION}, {PAJAMAS} {CAPE}, bursts through enormous fluffy pink and gold sunset clouds, cloud wisps "
        "swirling around him, exhilarated.", dream=True)),
    dict(id="s15d", p=1, beats=["moon"], reuse="v3/review/A5_dream_flight_s1.png"),
    dict(id="s15e", p=1, beats=["stars", "faster"], prompt=P(
        f"{ORION}, {PAJAMAS} {CAPE}, streaks across a vast starry night sky full of glittering stars and a "
        "glowing purple and blue galaxy, flying faster and faster, a trail of sparkling light behind him.",
        dream=True)),
    # ---- 16  Shoes on the Wire
    dict(id="s16a", p=1, beats=["fast", "shoes"], prompt=P(
        "Close-up in a starry dream sky: a pair of small red canvas sneakers with loose untied laces slipping "
        "off a flying boy's feet, the laces fluttering in the rushing wind, his pajama legs and red cape "
        "visible, magical starlight.", dream=True)),
    dict(id="s16b", p=1, beats=["laces"], prompt=P(
        "A pair of small red canvas sneakers tumbling down through a soft dawn sky toward a quiet suburban "
        "street far below, laces streaming, pink and gold sunrise.", dream=True)),
    dict(id="s16c", p=1, beats=["wire", "why"], prompt=P(
        f"Early morning: a pair of small red canvas sneakers tied together by the laces hangs from a telephone "
        f"wire above a quiet autumn street in front of {HOUSE}, soft pink dawn light, maple leaves drifting.")),
    dict(id="s16d", p=2, beats=["why"], prompt=P(
        "Wide view down a long leafy autumn street at sunrise with wooden telephone poles, several pairs of "
        "different kids' sneakers hanging from the telephone wires all along the street, magical and "
        "whimsical, soft golden light.")),
    # ---- 17  The Boy Who Could Fly
    dict(id="s17a", p=1, beats=["known", "adventures"], prompt=P(
        f"{ORION}, {PAJAMAS} {CAPE}, flies happily through a breathtaking dreamscape of floating islands, "
        "waterfalls in the sky and soaring birds, adventurous and joyful, golden light.", dream=True)),
    dict(id="s17b", p=1, beats=["remember", "worth", "end"], prompt=P(
        f"Morning on {YARD}: {ORION}, {DAY_CLOTHES} but in his socks with no shoes, looks up with a knowing "
        "smile at his red sneakers hanging from the telephone wire above the street, soft golden morning "
        "light, leaves drifting down, heartwarming.")),
]
