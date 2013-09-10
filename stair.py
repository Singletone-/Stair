#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""module for finding a chains similar words.

similar words:
    1) word a and b is called similar if Hamming distance from a to b is 1.
    2) word a and b is called similar if Levenshtein distance from a to b is 1.
Module are allowed to find all similar word for given, iterate for all words,
caching and add words by dynamically. And it's all as a graph of words.
"""

__all__ = [
    'WordGraph',
    'DiffLenGraph',
    'load_dict_from_file',
]

from itertools import filterfalse
from collections import deque
from hashlib import sha256 as hash_alg_1

class hash_alg:
    state = 0
    string = '' 
    def __init__(this):
        #сначала грузим потом сохраняем
        this.file = open('out.txt', 'ta+', encoding = 'utf-8')
        this.s = []

    def update(this, s):
        this.s.append(s)

    def hexdigest(this):
        if hasattr(this, 'hex_s'):
            return this.hex_s
        this.s = b''.join(this.s)
        this.hex_s = hash_alg_1(this.s).hexdigest()
        
        print(len(this.s), file =this.file)
        if hash_alg.string:
            print(hash_alg.string == this.s, file=this.file)
        else:
            hash_alg.string = this.s
        print(this.s[:20], file = this.file)
        print(this.s[-20:], file = this.file)
        print(this.hex_s, file = this.file)
        this.file.close()
        return this.hex_s        
    

class WordGraph(dict):
    #Graph similar words based on the Hamming distance(1 meaning)
    def __init__(self, alph = ''):
        self.alph = set(alph)
        super().__init__(self)
    def __delitem__(self, key):
        for wrd in self[key]:
            self[wrd].discard(key)
        super().__delitem__(self, key)
    def __setitem__(self, key, val):
        raise NotIplemented("What else do you want?!:)")

    def iter(self, wrd):
        """generator of similar on wrd  words \
            генератор слов похожих на wrd

        NB: It's not the same as __iter__
        """
        for i in range(len(wrd)):
            for letter in self.alph:
                #change one letter of word wrd at i-position
                yield wrd[:i] + letter + wrd[i+1:] 

    def find_links(self, edge):
        """find all similar words and return it

        find_links(self, key : string) -> [string]
        """
        self.alph.update(edge)
        res = set()
        for wrd in filter(self.__contains__, self.iter(edge)):
            self[wrd].add(edge)
            res.add(wrd)
        return res

    def add_edge(self, key):
        """add word in graph/Добавляем слово в граф

        add_edge(self, key : string) -> [string]
        Return a new edge in graph/Возвращает новый узел в графе
        """
        if key in self:
            return self[key]
        edges = self.find_links(key)
        super().__setitem__(key, edges)
        return edges
    def search_path(self, begword, endword):
        """Search shortest way from word to word
        (Поиск кратчайшего пути от узла begword до endword)

        graph.search_path(begword, endword) -> [str]
        if path is found raise KeyError
        exceptions:
            KeyError
        """
        if begword not in self:
            self.add_edge(begword)
        if endword not in self:
            self.add_edge(endword)
        if begword == endword:
            return [begword]

        tup = (begword,)
        queue, steps = deque((tup,)), set(tup)
        while queue:
            path = queue.popleft()            
            for link in filterfalse(steps.__contains__,  self[path[-1]]):
                new_path = path + (link,)
                if link == endword:
                    return new_path
                steps.add(link)
                queue.append(new_path)
        raise KeyError('Not Found: ' + endword)

    def save_cache(self, file):
        """save graph in file in text-like view and close it(optionally).

        save_cache(self, file_for_writing_or_filename)->None

        if second arg is filename, then it open for writing(delete if exist)
        and after all close it,
        another it will not closed.
        """
        flag = False
        if isinstance(file, str):
            flag = True
            try:
                file = open(file, mode='wt')
            except IOError:
                raise KeyError(file + " - not exist")

        k = self.keys()
        hash_code = hash_alg()
        for i in k:
            hash_code.update(i.encode())
        print(''.join(self.alph), file=file)
        print(hash_code.hexdigest(), file=file)
        for i in k:
            print(i, ' '.join(self[i]), file=file)
        if flag:
            file.close()
    def load_cache(self, file):
        """load graph in file in text-like view and close it(optionally).

        load_cache(self, file_for_reading_or_filename)->None

        (like save_cache)
        if second arg is filename, then it open for reading(delete if exist)
        and after all close it,
        another it will not be closed.
        raise ResourceWarning if file is invalid
        """
        if isinstance(file, str):
            try:
                file = open(file, mode='rt')
            except IOError:
                raise KeyError(file + " - not exist")
                if file is not None:
                    file.close()

        self.alph = set(file.readline().strip())
        hash_eqv = file.readline().strip()
        hash_code = hash_alg()

        for line in file:
            try:
                (name, *nodes) = line.split()
                hash_code.update(name.encode())
                super().__setitem__(name, set(nodes))
            except:
                pass
        file.close()
        if hash_eqv != hash_code.hexdigest():
            self.clear()
            raise ResourceWarning()


class DiffLenGraph(WordGraph):
    #Graph similar words based on the Levenshtein distance(2 meaning)
    def iter(self, wrd):
        """generator of similar on wrd  words
        (генератор похожих на wrd)

        NB: It's not the same as __iter__
        """
        for i in range(len(wrd)):
            yield wrd[:i] + wrd[i+1:]
            for letter in self.alph:
                #change one letter of word wrd at i-position
                yield wrd[:i] + letter + wrd[i+1:]


def load_graph_from_file(graph, filename): 
    """Загружаем  из файла словарь в граф похожих слов

    d.load_graph_from_file(filename-or-stream) -> None
    load_graph_from_file(graph, filename-or-stream) -> None

    if second arg is filename, then it open for reading(delete if exist)
    and after all close it,
    another it will not be closed.
    """
    if isinstance(filename, str):
        try:
            file = open(filename, mode='rt')
        except IOError:
            raise KeyError(filename + " - not exist")
            if file is not None:
                file.close()
    else:
        file = filename

    for line in file:
        graph.add_edge(line.strip())    
    file.close()
    return graph


def main():
    def get_cache_name(dict_name):        
        dict_name = path.realpath(dict_name)
        dict_name = path.splitext(path.split(dict_name)[-1])[0]
        return path.join(DICT_DIR, dict_name + '_' + args.mode)

    from argparse import ArgumentParser
    import os.path as path

    DICT_DIR = 'dict'
    DEF_DICT = r'runouns.txt'
    PROMPT_BEG = "Input a first word: "
    PROMPT_END = "Input a end word: "
    PATH_NOT_FOUND = "I can't find path"
    mode_help = """which kind of similar words will be used where
        word = the same-length words differ on 1 symbl
        diff = words differ on 1 or their length are different on 1 (default: word)
        """
    not_echo_help = r'not show prompts for before answer and reading(default: False)'
    save_help = 'save graph after exit(default: False)'
    dict_help = 'file which contains list of words'
    switch = {
        'word' : WordGraph,
        'diff' : DiffLenGraph
    }
    parser = ArgumentParser()    
    parser.add_argument('-m', '--mode', choices=switch,
        default='word', help=mode_help
    )
    parser.add_argument('-s', '--save',
        action='store_true', help=save_help
    )
    parser.add_argument('-n', '--not_echo',
        action='store_true', help=not_echo_help
    )
    parser.add_argument('-d', '--dict',
        type=str, default=DEF_DICT, help=dict_help
    )
    ####
    args = parser.parse_args()
    graph = switch[args.mode]();
    dict_cache = get_cache_name(args.dict)
    if path.exists(dict_cache):        
        try:
            graph.load_cache(dict_cache)
        except (KeyError, ResourceWarning):
            load_graph_from_file(graph, args.dict)
    else:
        load_graph_from_file(graph, args.dict)

    if args.not_echo:
        prompt2 = prompt1 = ''
    else:
        prompt1, prompt2 = PROMPT_BEG, PROMPT_END

    if args.save:
        graph.save_cache(dict_cache)

    try:
        while True:
            beg = input(prompt1).lower().strip()
            end = input(prompt2).lower().strip()

            try:
                print(' '.join(graph.search_path(beg, end)))
            except KeyError:
                print(PATH_NOT_FOUND)
    except (KeyboardInterrupt, SystemExit, EOFError):
        pass
        """
        if args.save:
            graph.save_cache(dict_cache)
        """

if __name__ == '__main__':
        main()
