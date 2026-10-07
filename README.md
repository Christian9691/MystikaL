Mystika ✦

A spell-casting programming language and a single-window desktop IDE for it. Mystika source is scanned into runes, woven into Python, and cast (executed) in a separate process. Runtime errors are reported against your Mystika line numbers, not the generated Python's.

The magic words are Encantadia-inspired: write abisala instead of if, brilyante instead of def, hayag instead of print.

Requirements
Python 3.10+
tkinter (bundled with most Python installs; on Debian/Ubuntu: sudo apt install python3-tk)
No third-party packages
Run
bash
python main.py
Usage
Action	How
Cast the spell (run)	✦ Cast Spell button or Ctrl+Enter
Indent / dedent	Tab inserts 4 spaces, Shift+Tab removes up to 4
Auto-indent	Pressing Enter keeps the indent, and adds 4 after a line ending in :
Load the demo program	📜 Sample button
Reset editor and output	🗑 Clear button
Insert a keyword	Double-click it in the Spellbook sidebar (selecting a row shows its meaning)

The right panel has two tabs: Result (program output, or a scanner error / traceback) and Python Form (the generated Python). The status bar shows ready / casting / nagtagumpay / pumalya.

Keywords (34 spells)
Daloy ng Mahika
Mystika	Python	Meaning
abisala	if	Abisala! Kung totoo ang kondisyon
eshma	elif	Isa pang kondisyon
ashti	else	Kung walang tumama
lireo	while	Umikot habang may bisa ang sumpa
sapiro	for	Isa-isang daanan ang koleksyon
hathoria	in	Nasa loob ng
lagot	break	Sirain ang ikot
tuloy	continue	Lumaktaw sa susunod na ikot
tahimik	pass	Walang gagawin
Katotohanan
Mystika	Python	Meaning
ivo	True	Pag-ibig, tama, totoo
hagorn	False	Kasamaan, mali, hindi totoo
adamya	None	Ang kawalan
emre	and	Dapat parehong tama
alena	or	Isa lang ay sapat na
pirena	not	Baligtarin ang bisa
Kapangyarihan
Mystika	Python	Meaning
brilyante	def	Lumikha ng bagong kapangyarihan (function)
bumalik	return	Ibalik ang resulta ng kapangyarihan
sanggre	class	Lahi ng mga nilalang (class)
Pagsubok
Mystika	Python	Meaning
hamon	try	Subukan ang mapanganib na gawain
bigo	except	Kapag nabigo ang hamon
wakas	finally	Laging mangyayari sa dulo
sumpain	raise	Magpakawala ng sumpa (error)
Pagtawag
Mystika	Python	Meaning
ipatawag	import	Tawagin ang panlabas na kapangyarihan
etheria	from	Mula sa anong kaharian
hayag	print	Ihayag ang mensahe
usisa	input	Magtanong sa nagbabasa
Anyo ng Datos
Mystika	Python	Meaning
buo	int	Buong bilang
hati	float	May decimal
titik	str	Teksto
tadhana	bool	Totoo o hindi
hanay	list	Maayos na koleksyon
tali	tuple	Koleksyon na hindi mababago
natatangi	set	Koleksyon na walang pareho
aklat	dict	Susi at halaga

Everything else is plain Python syntax (range, len, operators, f-strings, and so on).

Example
brilyante bati(pangalan):
    bumalik "Abisala, " + pangalan

hayag(bati("eshma"))

More programs are in examples/: hello.mys, loops.mys, trials.mys and error_demo.mys (shows error line remapping). Open one in any text editor and paste it into the IDE to try it.

How it works
source text ──▶ scanner ──▶ runes ──▶ weaver ──▶ Python + line map ──▶ caster ──▶ output
Scanner reads the text character by character and produces runes. A bad character or an unclosed string stops here, with the line and column.
Weaver swaps each spell for its Python equivalent and records which Mystika line every Python line came from.
Caster runs the Python in a subprocess with a time limit, then rewrites the traceback line numbers using the line map.
Known limitations
Spells are reserved words outside strings and comments. A variable named ivo or hati is treated as the spell. (After a dot, such as obj.hati, it stays a normal name.)
Scripts are stopped after 10 seconds and reported as timed out.
usisa (input) cannot read from the keyboard; the script gets no input and will raise an error.
Spells are defined in spellbook.py. There is no file save/open or multi-file support.
The IDE runs your code with your Python interpreter and user permissions. Only run code you trust.
Tests
bash
python -m unittest discover tests

GUI tests need a display and are skipped automatically when none is available (on a headless machine use xvfb-run python -m unittest discover tests).

Docs
docs/SPEC-Mystika.md: the language definition
docs/DESIGN.md: architecture and design decisions
docs/DEMO.md: 5-minute demo script and likely questions
Project layout
File	Role
spellbook.py	GRIMOIRE (grouped spells) and SPELLBOOK (flat lookup)
scanner.py	scan() returns runes, or a scanner problem with line and column
weaver.py	weave() returns Python source and a line map
caster.py	cast() runs a subprocess with timeout and traceback remapping
studio.py	tkinter IDE (MystikaStudio)
main.py	entry point
examples/	sample .mys programs
tests/	unit, end-to-end and GUI tests
docs/	spec, design notes, demo script
