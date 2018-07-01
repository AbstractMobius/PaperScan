import random
import re
import nltk
from docx import Document
from gensim.models.keyedvectors import KeyedVectors

class PaperScanner:
    def __init__(self):
        pass
        # this is a 3.6 gigabyte file that needs to be downloaded at
        # https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit
        self.word_vectors = KeyedVectors.load_word2vec_format(
        '/home/intel/PycharmProjects/PaperScan/GoogleNews-vectors-negative300.bin', binary=True).wv

    def compare(self, file_name1, file_name2):
        file1 = paper._clean_doc(file_name1)
        file2 = paper._clean_doc(file_name2)
        return paper._generate_couples(file1, file2)

    def _remove_pairs(self, ocl, ocr, comp_dict):
        delete = []
        for i in comp_dict.keys():
            val, val1 = comp_dict[i].split(":")[0], comp_dict[i].split(":")[1]
            if int(val) in ocl or int(val1) in ocr:
                delete.append(i)
        for i in delete:
            del comp_dict[i]
        return comp_dict

    def _determine_paragraph_similarity(self, compared_paragraphs, size):
        comparison_dict = {}
        for i in compared_paragraphs.keys():
            comparison_dict[i] = 0
            for k in compared_paragraphs[i]:
                comparison_dict[i] += k
        r_comp_dict = {}
        for i in comparison_dict.keys():
            if comparison_dict[i] not in r_comp_dict:
                r_comp_dict[comparison_dict[i]] = i
            else:
                r_comp_dict[comparison_dict[i] + random.uniform(0, 1)] = i
        maxim = list(r_comp_dict.keys())
        maxim.sort(reverse=True)
        comparables_left = True
        occupiedl = []
        occupiedr = []
        paired = []
        while comparables_left:
            val = r_comp_dict[maxim[0]].split(":")
            paired.append(r_comp_dict[maxim[0]])
            m, n = int(val[0]), int(val[1])
            occupiedl.append(m)
            occupiedr.append(n)
            r_comp_dict = self._remove_pairs(occupiedl, occupiedr, r_comp_dict)
            maxim = list(r_comp_dict.keys())
            maxim.sort(reverse=True)
            comparables_left = len(r_comp_dict.keys()) > 1
            if not comparables_left and len(r_comp_dict.keys()) == 1:
                paired.append(r_comp_dict[maxim[0]])
        r_pair = paired
        new_solice = []
        if len(r_pair) < size:
            for i in r_pair:
                tmp = i.split(":")
                if int(tmp[0]) != int(tmp[1]):
                    new_solice.append(tmp[1] + ":" + tmp[0])
        value = 0
        p = paired + new_solice
        for i in p:
            value += comparison_dict[i]
        return value

    def _get_similarity_scores(self, word_list1, word_list2):
        word_combinations = {}
        index_combinations = []
        scores = []
        for i in range(len(word_list1)):
            for j in range(len(word_list2)):
                sorted_words = [word_list1[i], word_list2[j]].sort()
                if sorted_words in word_combinations.keys():
                    score = word_combinations[sorted_words]
                else:
                    score = self.word_vectors.wv.similarity(word_list1[i], word_list2[i])
                    word_combinations[sorted_words] = score

                index_combinations.append((score, i, j))

        index_combinations.sort()
        while len(index_combinations) != 0:
            scores.append(index_combinations[0][0])
            index_combinations = [edge for edge in index_combinations if
                                  (edge[1] != index_combinations[0][1]) and (edge[2] != index_combinations[0][2])]

        return scores

    def _generate_couples(self, paragraph_dicts1, paragraph_dicts2):
        if len(paragraph_dicts1.keys()) >= len(paragraph_dicts2.keys()):
            paragraph_iterator = len(paragraph_dicts2.keys())
        else:
            paragraph_iterator = len(paragraph_dicts1.keys())
        couples = {}
        for i in range(paragraph_iterator):
            for k in range(paragraph_iterator):
                couples[str(i)+ ":" +str(k)] = []
        analyzed = []
        words1 = 0
        for i in paragraph_dicts1:
            for k in paragraph_dicts1[i]:
                for j in paragraph_dicts1[i][k]:
                    words1 += 1
        words2 = 0
        for i in paragraph_dicts2:
            for k in paragraph_dicts2[i]:
                for j in paragraph_dicts2[i][k]:
                    words2 += 1
        words = 0
        if words1 <= words2:
            words = words1
        else:
            words = words2
        for i in range(paragraph_iterator):
            for k in range(paragraph_iterator):
                val = [i, k]
                val.sort()
                if val not in analyzed:
                    analyzed.append(val)
                    par1 = paragraph_dicts1[i]
                    par2 = paragraph_dicts2[k]
                    for ioc in par1:
                        coupled = self._get_similarity_scores(par1[ioc], par2[ioc])
                        for j in coupled:
                            couples[str(i) + ":" + str(k)].append(j)
                else:
                    del couples[str(i) + ":" + str(k)]
        value1 = self._determine_paragraph_similarity(couples, paragraph_iterator)
        return value1/words

    def _paragraph_to_dictionary(self, paragraph):
        parts_of_speech = {"Noun":[], "Verb":[], "Adjective":[]}
        for sentence in paragraph:
            for word, pos in sentence:
                valid, ext = self._get_ioc(pos)
                if valid:
                    parts_of_speech[ext].append(word)
        return parts_of_speech


    def _clean_paragraph(self, doc):
        parsed_paragraph_1 = []
        sentences = doc.text.split('.')
        for i in range(len(sentences)):
            parsed_paragraph_1.append([])
            content = sentences[i].split(' ')
            for k in range(len(content)):
                if content[k] != '':
                    try:
                        parsed_paragraph_1[i].append(
                            nltk.pos_tag(nltk.word_tokenize(re.sub(r'\W+', '', content[k])))[0])
                    except IndexError:
                        pass
        return self._paragraph_to_dictionary(
            parsed_paragraph_1[:len(parsed_paragraph_1)-1])

    def _clean_doc(self, doc):
        document = Document(doc)
        pars = document.paragraphs
        correction = 0
        content_pars1 = {}
        for body in range(len(pars)):
            content = self._clean_paragraph(pars[body])
            if content != {"Noun":[], "Verb":[], "Adjective":[]}:
                content_pars1[body - correction] = content
            else:
                correction += 1
        return content_pars1

    def _get_ioc(self, val):
        ioc = {"Noun": ["NN", "NNS", "NNP", "NNPS"],
               "Verb": ["VBZ", "RB", "RBR", "RBS",
                  "VBD", "VBG", "VBN", "VBP", "VBZ", "WRB"],
               "Adjective": ["JJ", "JJR", "JJS"]}
        for i in list(ioc.keys()):
            if val in ioc[i]:
                return True, i
        return False, ""




