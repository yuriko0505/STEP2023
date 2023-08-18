/*
***usage***

$ g++ -o prob_1 prob_1.cpp
$ ./prob_1 <path of input file> <path of output file>
*/


#include <bits/stdc++.h>
using namespace std;

vector<pair<string, string> > sorted_dictionary;

void compile_sorted_dictionary();
string find_anagram(string word);

int main(int argc, char *argv[]){
    ifstream fin(argv[1]);
    ofstream fout(argv[2]);

    string str;

    compile_sorted_dictionary();

    if (!fin) {
        cout << "Failed to open file." << endl;
        return -1;
    }

    while(getline(fin, str)){
        fout << find_anagram(str) << endl;
    }

    return 0;
}

void compile_sorted_dictionary(){
    const string filename = "../anagram/words.txt";
    ifstream fin(filename);

    string word;

    if (!fin) {
        cout << "Failed to open " << filename << endl;
        exit(EXIT_FAILURE);
    }

    while(getline(fin, word)){
        string sorted = word;
        sort(sorted.begin(), sorted.end());
        sorted_dictionary.__emplace_back(make_pair(sorted, word));
        //sorted_dictionary.emplace_back({sort(word.begin(), word.end()), word});
    }

    sort(sorted_dictionary.begin(), sorted_dictionary.end());
}

string find_anagram(string word){
    string sorted_word = word;
    sort(sorted_word.begin(), sorted_word.end());
    int begin = 0, end = sorted_dictionary.size();
    while(begin+1 < end){
        int temp = (begin + end) / 2;
        int judge = sorted_dictionary[temp].first.compare(sorted_word);
        //cout << judge << " " << sorted_dictionary[temp].first << " " << sorted_word << endl;
        if(judge < 0){
            begin = temp;
        }else if(judge > 0){
            end = temp;
        }else{
            return sorted_dictionary[temp].second;
        }
    }

    return "not found";
}