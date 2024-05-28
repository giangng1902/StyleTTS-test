from xml.dom import minidom
import re

ignore_word = ["_", "'", ";", ".", ")", "(", ":", "?", "!", "...", "\"", "[", "]", "*", "/", "\\", ",", "-"]
vowels_list_origin = ['a' , 'E', 'e', 'i', 'O', 'o', '7', 'u', 'M', 'a_X', '7_X', 'E_X', 'O_X', 'ie', 'uo', 'M7']
_tone_map = {
    "": "1", "1": "1", "2": "2", "3": "3", "4": "4",
    "5a": "5", "5b": "6", "6a": "7", "6b": "8"
}
_phoneme_map = {
    "a": "a",# a
    "E": "E",# e
    "e": "e",# ê
    "i": "i",# i/y 
    "O": "O",# o
    "o": "o",# ô
    "7": "9",# ơ
    "u": "u",# u
    "M": "M",# ư
    "a_X": "aX",# ă
    "7_X": "9X",# â
    "E_X": "EX",# a (rách)
    "O_X": "OX",# o (hỏng)
    "ie": "ie",# iê (hiếm)
    "uo": "uo",# uô (chuối)
    "M7": "M9",# ươ (mươi)
    "b": "b",# b
    "d": "d",# đ
    "s": "s",# x (xu)
    "S": "S",# s (su)
    "G": "G",# g (gan)
    "x": "x",# kh (khánh)
    "l": "l",# l
    "v": "v",# v
    "t_h": "th",# th
    "z": "z",# d
    "f": "f",# ph (phai)
    "ts\\": "ts",# ch
    "tS": "tS",# tr
    "h": "h",# h
    "k": "k",# ch (rách) / q (qua) / c (cú, liếc)
    "t": "t",# t
    "p": "p",# p
    "n": "n",# n
    "kp": "kp",# c (lóc)
    "m": "m",# m
    "N_+": "Np",# nh after i,ê,a (not )
    "J": "J",# nh (hình)
    "j": "j",# i (mươi) / y (cay)
    "N": "N",# ng (hạng)
    "Nm": "Nm",# ng (lủng, hỏng)
    "wp": "wp",# o (thoa)  / u (qua, tuyên)
    "dZ": "dZ",# gi (giao)
    "w": "w",# o (giao)
    "r": "r",# r
}


def get_word(word_tag, use_phoneme):
    if not use_phoneme:
        return word_tag.childNodes[0].data.strip()
    syllables_tag = word_tag.getElementsByTagName("syllable")
    if len(syllables_tag) == 0:
        return None, None, None, None

    phonemes, phonemes_space, words = "", "", ""
    for syllable_tag in syllables_tag:
        word, tone, tmp = "", "", ""
        if "tone" in syllable_tag.attributes:
            tone = syllable_tag.attributes["tone"].value

        ### fix the case: null in syllable tag ###
        syllable_value = syllable_tag.attributes.get("ph")
        syllable_value = syllable_value.value if syllable_value else None
        if (
            syllable_value 
            and syllable_value.strip() == "n u l l" 
            and "null" in word_tag.attributes['ph'].value
        ):
            continue

        phonemes_tag = syllable_tag.getElementsByTagName("ph")
        for i, phoneme_tag in enumerate(phonemes_tag):
            phoneme_value = phoneme_tag.attributes["p"].value
            if i == 0 and phoneme_value not in vowels_list_origin:
                word += phoneme_value
                phonemes += phoneme_value + " "
                tmp += phoneme_value + " "
            else:
                word += phoneme_value + tone
                phonemes += phoneme_value + tone + " "
                tmp += phoneme_value + tone + " "
        words += " " + word
        phonemes_space += tmp + "- "
    return (
        words.strip(), 
        phonemes.strip(), 
        phonemes_space.strip(), 
        phonemes_space.strip()[:-1] + "#"
    )


def get_word_nodes(node):
    words_tag = []

    for node in node.childNodes:
        try:
            if node.tagName == "t" or node.tagName == "boundary":
                words_tag.append(node)
            else:
                words_tag.extend(get_word_nodes(node))
        except AttributeError:
            pass

    return words_tag


def get_content(xml_content, use_phoneme=True):
    # xml_doc = minidom.parseString(xml_content)
    xml_doc = open(xml_content, "r")
    xml_doc = minidom.parseString(xml_doc)
    print(xml_doc)
    sentence_char = sentence_phone = ""
    sentence_phone_space = sentence_phone_word = ""
    phrases_tag = list(xml_doc.getElementsByTagName("p"))
    words_tag = []
    for ph in phrases_tag: 
        words_tag.extend(get_word_nodes(ph))

    words=[] #
    last_t_tag = None
    sil_elements = []
    for word_tag in words_tag:
        if word_tag.tagName != "boundary":
            ### assign new last tag to this tag ###
            last_t_tag = word_tag
            # print(word_tag.getElementsByTagName("syllable")[0].attributes.get('ph').value)
            (
                word_char, 
                phone_char, 
                phone_char_space,
                phone_char_word
            ) = get_word(word_tag, use_phoneme)
            print(get_word(word_tag, use_phoneme)[0])
            if word_char:
                sentence_char += " " + word_char
            if phone_char:
                sentence_phone += " " + phone_char
                sentence_phone_space += " " + phone_char_space
                sentence_phone_word += " " + phone_char_word
                
                word = word_tag.childNodes[0].data.lower().strip()
                
                words.extend([i for i in re.split('-| |#|sp', word) if i != ''])#
        else:
            ### remember the previous tag of this boundary tag ###
            prev_t_character = None
            if last_t_tag:
                prev_t_character = last_t_tag.childNodes[0].data.lower().strip()
                prev_t_character = re.sub("\.+", ".", prev_t_character)
            word_tag.prev_t_character = prev_t_character
            sil_elements.append(word_tag)

            ### add sp (silence) to phoneme sequence ###
            if sentence_char.strip() and sentence_char.strip()[-1] != ",":
                sentence_char += ","
            if sentence_phone.strip() and sentence_phone.strip()[-2:] != "sp":
                sentence_phone += " sp"
                sentence_phone_space += " sp"
                sentence_phone_word += " sp"

    if sentence_phone_space and sentence_phone_space[-2:] == "sp":
        sentence_phone_space = sentence_phone_space[:-2]
        # TODO: fix later
        # if "lantrinh" in os.environ.get("LIB_CONFIGS_KEY", ""):
        #     sentence_phone_word = sentence_phone_word[:-2]

    last_character = None
    if last_t_tag:
        last_character = last_t_tag.childNodes[0].data.lower().strip()
        last_character = re.sub("\.+", ".", last_character)
    
    if sentence_phone_word.strip() == "":
        sentence_phone_word = "sp"

    return (
        words,#
        [i for i in re.split('-|sp', sentence_phone_space) if i != '' and i != ' '],
        last_character,
        sil_elements,
        sentence_char, 
        "{" + sentence_phone.strip() + "}", 
        "{" + sentence_phone_space.strip() + "}",
        "{" + sentence_phone_word.strip() + "}"
    )

if __name__ == "__main__":

    print(
        get_content(r"C:/lantrinh/lantrinh/prompt_allophones/0001.xml")
    )