GRIMOIRE: dict[str, list[tuple[str, str, str]]] = {
    "Daloy ng Mahika": [
        ("abisala",   "if",       "Abisala! Kung totoo ang kondisyon"),
        ("eshma",     "elif",     "Isa pang kondisyon"),
        ("ashti",     "else",     "Kung walang tumama"),
        ("lireo",     "while",    "Umikot habang may bisa ang sumpa"),
        ("sapiro",    "for",      "Isa-isang daanan ang koleksyon"),
        ("hathoria",  "in",       "Nasa loob ng"),
        ("lagot",     "break",    "Sirain ang ikot"),
        ("tuloy",     "continue", "Lumaktaw sa susunod na ikot"),
        ("tahimik",   "pass",     "Walang gagawin"),
    ],
    "Katotohanan": [
        ("ivo",       "True",     "Pag-ibig, tama, totoo"),
        ("hagorn",    "False",    "Kasamaan, mali, hindi totoo"),
        ("adamya",    "None",     "Ang kawalan"),
        ("emre",      "and",      "Dapat parehong tama"),
        ("alena",     "or",       "Isa lang ay sapat na"),
        ("pirena",    "not",      "Baligtarin ang bisa"),
    ],
    "Kapangyarihan": [
        ("brilyante", "def",      "Lumikha ng bagong kapangyarihan (function)"),
        ("bumalik",   "return",   "Ibalik ang resulta ng kapangyarihan"),
        ("sanggre",   "class",    "Lahi ng mga nilalang (class)"),
    ],
    "Pagsubok": [
        ("hamon",     "try",      "Subukan ang mapanganib na gawain"),
        ("bigo",      "except",   "Kapag nabigo ang hamon"),
        ("wakas",     "finally",  "Laging mangyayari sa dulo"),
        ("sumpain",   "raise",    "Magpakawala ng sumpa (error)"),
    ],
    "Pagtawag": [
        ("ipatawag",  "import",   "Tawagin ang panlabas na kapangyarihan"),
        ("etheria",   "from",     "Mula sa anong kaharian"),
        ("hayag",     "print",    "Ihayag ang mensahe"),
        ("usisa",     "input",    "Magtanong sa nagbabasa"),
    ],
    "Anyo ng Datos": [
        ("buo",       "int",      "Buong bilang"),
        ("hati",      "float",    "May decimal"),
        ("titik",     "str",      "Teksto"),
        ("tadhana",   "bool",     "Totoo o hindi"),
        ("hanay",     "list",     "Maayos na koleksyon"),
        ("tali",      "tuple",    "Koleksyon na hindi mababago"),
        ("natatangi", "set",      "Koleksyon na walang pareho"),
        ("aklat",     "dict",     "Susi at halaga"),
    ],
}

# Flat lookup used by the scanner and the weaver.
SPELLBOOK: dict[str, str] = {
    word: py
    for entries in GRIMOIRE.values()
    for word, py, _hint in entries
}