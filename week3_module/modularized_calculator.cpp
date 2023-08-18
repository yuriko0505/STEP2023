#include <algorithm> // find
#include <cmath> // abs, round
#include <iostream>
#include <limits> // quiet_NaN
#include <string>
#include <vector>

using namespace std;

// Token types
enum type_of_token{
    NUMBER,
    // operators
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    // delimiters
    LEFT,
    RIGHT,
    // cast functions
    ABS,
    INT,
    ROUND,
    // typo
    TYPO
};

// {type, number}
// If it is not a value, nothing is assigned to "number".
struct token{
    type_of_token type;
    double number;
};


token read_number(string line, size_t& index);
token read_operator_and_delimiter(string line, size_t& index);
token read_castfunction(string line, size_t& index);
bool tokenize(string line, vector<token>& tokens);
double evaluate(const vector<token>& tokens);
double evaluate_term(const vector<token>& tokens, size_t& token_index);
double evaluate_expression(const vector<token>& tokens, size_t& token_index);
double evaluate_atom(const vector<token>& tokens, size_t& token_index);
void test(string line, double actual_answer);
void run_test();

int main(){
    run_test();
    string line;
    while(true){
        cout << "> ";
        getline(cin, line);
        vector<token> tokens;
        if(!tokenize(line, tokens)){
            cout << "try again :)" << endl;
            continue;
        }
        double answer = evaluate(tokens);
        cout << "answer = " << answer << endl;
    }
    
    return 0;
}

token read_number(string line, size_t& index){
    double number = 0;
    size_t len_of_line = line.size();
    while (index < len_of_line && isdigit(line[index])){
        number = number * 10 +  (line[index] - '0');
        index++;
    }
    if (index < len_of_line && line[index] == '.'){
        index++;
        double decimal = 0.1;
        while (index < len_of_line && isdigit(line[index])){
            number += (line[index] - '0') * decimal;
            decimal /= 10;
            index++;
        }
    }
    token temp = {.type = NUMBER, .number = number};
    return temp;
}

token read_operator_and_delimiter(string line, size_t& index){
    token temp;
    switch(line[index]){
        case '+':
            temp.type = PLUS;
            break;
        case '-':
            temp.type = MINUS;
            break;
        case '*':
            temp.type = MULTIPLY;
            break;
        case '/':
            temp.type = DIVIDE;
            break;
        case '(':
            temp.type = LEFT;
            break;
        case ')':
            temp.type = RIGHT;
            break;
    }
    index++;
    return temp;
}

bool is_operator_or_delimiter(char c){
    return (c >= 40 && c <= 47 && c != 44 && c != 46);
}

token read_castfunction(string line, size_t& index){
    token temp = {.type = TYPO};
    if (line[index] == 'a'){
        index++;
        if (line[index] == 'b'){
            index++;
            if (line[index] == 's'){
                temp.type = ABS;
                index++;
                return temp;
            }
        }
    } else if (line[index] == 'i'){
        index++;
        if (line[index] == 'n'){
            index++;
            if (line[index] == 't'){
                temp.type = INT;
                index++;
                return temp;
            }
        }
    } else if (line[index] == 'r'){
        index++;
        if (line[index] == 'o'){
            index++;
            if (line[index] == 'u'){
                index++;
                if (line[index] == 'n'){
                    index++;
                    if (line[index] == 'd'){
                        temp.type = ROUND;
                        index++;
                        return temp;
                    }
                }
            }
        }
    }
    return temp;
}

// Split the line into a list of tokens.
// If the line contains invalid characters,
//     output an error statement and return false.
bool tokenize(string line, vector<token>& tokens){
    size_t index = 0;
    size_t len_of_line = line.size();
    token token_temp;
    while (index < len_of_line){
        if (isdigit(line[index])){
            token_temp = read_number(line, index);
        } else if (is_operator_or_delimiter(line[index])){
            token_temp = read_operator_and_delimiter(line, index);
        } else if (line[index] >= 97 && line[index] <= 122){
            token_temp = read_castfunction(line, index);
            if(token_temp.type == TYPO){
                printf("ERROR: unsupported functions or typo\n");
                return false;
            }
        } else if (line[index] == ' '){
            index++;
            continue;
        } else {
            printf("ERROR: invalid character found: \"%c\" (index %zu)\n", line[index], index);
            return false;
        }
        tokens.emplace_back(token_temp);
    }
    return true;
}

// Evaluate the token lists.
// Calculate from addition and subtraction first.
double evaluate(const vector<token>& tokens){
    size_t token_index = 0;
    size_t num_of_tokens = tokens.size();
    double answer = evaluate_expression(tokens, token_index);
    
    // Return an error if the final token_index does not match the number of tokens.
    if (token_index != num_of_tokens){
        cout << "something wrong :(" << endl;
        return numeric_limits<double>::quiet_NaN();
    }
    return answer;
}

// <expression> ::= <term> (( + | - ) <term>)*
// Adding and Subtracting
// Calculate from multiplication and division.
// Return the next index after the last term linked by '+' or '-'.
double evaluate_expression(const vector<token>& tokens, size_t& token_index){
    size_t num_of_tokens = tokens.size();
    double result = evaluate_term(tokens, token_index);
    while (token_index < num_of_tokens && (tokens[token_index].type == PLUS || tokens[token_index].type == MINUS)){
        if (tokens[token_index].type == PLUS){
            token_index++;
            result += evaluate_term(tokens, token_index);
        } else {
            token_index++;
            result -= evaluate_term(tokens, token_index);
        }
    }
    return result;
}

// <term> ::= <atom> (( * | / ) <atom>)*
// Multiplication and division.
// First, check if parentheses are included.
// Return the next index after the last term linked by '*' or '/'.
double evaluate_term(const vector<token>& tokens, size_t& token_index){
    double result = evaluate_atom(tokens, token_index);
    
    size_t num_of_tokens = tokens.size();
    while (token_index < num_of_tokens && (tokens[token_index].type == MULTIPLY || tokens[token_index].type == DIVIDE)){
        token_index++;
        if (tokens[token_index-1].type == MULTIPLY){
            result *= evaluate_atom(tokens, token_index);
        } else {
            double divisor = evaluate_atom(tokens, token_index);
            if (divisor == 0){
                cout << "ERROR: divide by zero" << endl;
                return numeric_limits<double>::quiet_NaN();
            }
            result /= (1.0 * divisor);
        }
    }
    return result;
}

// <atom> ::= n | <castfunction> | ( expression )
// <castfunction> ::= abs(expression) | int(expression) | round(expression)
// "n" means numerical value.
// Check if parentheses are included
// Calculate the contents of parentheses with the evaluate_expression function.
// Return NaN in case of grammatical errors
double evaluate_atom(const vector<token>& tokens, size_t& token_index){
    size_t cast_index = -1;
    token_index++;
    if (tokens[token_index-1].type == NUMBER){
        return tokens[token_index-1].number;
    } else if (tokens[token_index-1].type >= PLUS && tokens[token_index-1].type <= DIVIDE){
        if (token_index >= 2 && (tokens[token_index-2].type >= PLUS && tokens[token_index-2].type <= DIVIDE)){
            printf("ERROR: consecutive operators (token index: %zu)\n", token_index-1);
            return numeric_limits<double>::quiet_NaN();
        }
        token_index--;
        return 0;
    } else if (tokens[token_index-1].type >= ABS && tokens[token_index-1].type <= ROUND){
        cast_index = token_index-1;
        token_index++;
    }
    if (tokens[token_index-1].type == LEFT){
        double result = evaluate_expression(tokens, token_index);
        if (tokens[token_index].type == RIGHT){
            token_index++;
            if (cast_index == -1){
                return result;
            }
            switch(tokens[cast_index].type){
                case ABS:
                    return abs(result);
                case INT:
                    return int(result);
                case ROUND:
                    return round(result);
                default:
                    return result;
            }
        }
        cout << "ERROR: missing closing bracket" << endl;
        return numeric_limits<double>::quiet_NaN();
    } else {
        cout << "ERROR: missing opening bracket" << endl;
        return numeric_limits<double>::quiet_NaN();
    }
}

void test(string line, double actual_answer){
    vector<token> tokens;
    tokenize(line, tokens);
    double expected_answer = evaluate(tokens);
    if (abs(actual_answer - expected_answer) < 1e-8){
        printf("PASS! %s = %f\n", line.c_str(), expected_answer);
    } else {
        printf("FAIL! %s should be %f but was %f\n", line.c_str(), actual_answer, expected_answer);
    }
    return;
}

void run_test(){
    cout << "==== Test started! ====" << endl;
    test("11", 11);
    test("2+3", 5);
    test("22/7", 22.0/7.0);
    test("2*3-4/5-6*7+8/9", 2*3-4.0/5.0-6*7+8.0/9.0);
    test("9.80665", 9.80665);
    test("1.1+2.2", 3.3);
    test("1.1/2.2", 0.5);
    test("1.1*2.2-3.3*4.4-5.5/6.6+7.7/8.8", 1.1*2.2-3.3*4.4-5.5/6.6+7.7/8.8);
    test("(1+2)", 3);
    test("((1))", 1);
    test("(3.0 + 4 * (2 - 1)) / 5", (3.0 + 4 * (2 - 1)) / 5.0);
    test("(1+2)*3-4/(5-(6-7*8+9/(10-11)*12))", 8.97546012);
    test("(1.1+2.2)*3.3-4.4/(5.5-(6.5-7.7*8.8+9.9/(10.0-11.1)*12.2))", (1.1+2.2)*3.3-4.4/(5.5-(6.5-7.7*8.8+9.9/(10.0-11.1)*12.2)));
    test("abs(-273)", 273);
    test("int(3.14)", 3);
    test("round(-5.7)", -6);
    test("abs(((((-1)))))", 1);
    test("int(1)*(round(2.3)/abs(4-5*6))", 1.0/13.0);
    test("12 + abs(int(round(-1.55) + abs(int(-2.3 + 4))))", 13);
    cout << "==== Test finished! ====" << endl;
    return;
}