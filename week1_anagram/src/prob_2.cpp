/*
***usage***

$ g++ -o prob_2 prob_2.cpp
$ ./prob_2 <path of input file> <path of output file>
*/


#include <bits/stdc++.h>
using namespace std;

int SCORES[26] = {1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4};

struct word_comp{
    string original_word;
    int score;
    vector<int> letters;
};

vector<word_comp> counted_dictionary;

word_comp make_word_comp(string word);
void compile_counted_dictionary();
string find_anagram(string word);

int main(int argc, char *argv[]){
    clock_t start = clock();

    ifstream fin(argv[1]);
    ofstream fout(argv[2]);

    string str;

    compile_counted_dictionary();

    if (!fin) {
        cout << "Failed to open file." << endl;
        return -1;
    }

    while(getline(fin, str)){
        fout << find_anagram(str) << endl;
    }

    clock_t end = clock();

    cout << (end - start) * 1000 / CLOCKS_PER_SEC << "ms" << endl;

    return 0;
}

word_comp make_word_comp(string word){
    word_comp temp;
    temp.original_word = word;
    temp.score = 0;
    vector<int> letter_count(26, 0);
    for(char w: word){
        letter_count[w - 'a']++;
        temp.score += SCORES[w - 'a'];
    }
    temp.letters = letter_count;

    return temp;
}

void compile_counted_dictionary(){
    const string filename = "../anagram/words.txt";
    ifstream fin(filename);

    string word;

    if (!fin) {
        cout << "Failed to open " << filename << endl;
        exit(EXIT_FAILURE);
    }

    while(getline(fin, word)){
        word_comp temp = make_word_comp(word);
        counted_dictionary.__emplace_back(temp);
    }

    sort(counted_dictionary.begin(), counted_dictionary.end(),
        [](const word_comp& a, const word_comp& b) {return a.score > b.score;});
}

string find_anagram(string word){
    word_comp temp_word = make_word_comp(word);
    size_t size_of_dict = counted_dictionary.size();

    //int score_max = -1;
    //int score_max_index = -1;
    for(size_t i=0; i<size_of_dict; i++){
        //int score_temp = 0;
        for(int c=0; c<26; c++){
            if(counted_dictionary[i].letters[c] > temp_word.letters[c]){
                //score_temp = 0;
                break;
            }
            if(c == 25){
                return counted_dictionary[i].original_word;
            }
            //score_temp += SCORES[c] * counted_dictionary[i].letters[c];
        }
        // if(score_temp > score_max){
        //     score_max = score_temp;
        //     score_max_index = i;
        // }
    }

    return "not found";
    //return (score_max_index == -1)? "not found" : counted_dictionary[score_max_index].original_word;
}