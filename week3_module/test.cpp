#include <iostream>
#include <limits>
#include <optional>
using namespace std;

int main(){
    double a = 8;
    optional<double> b;
    // b.value() *= numeric_limits<double>::quiet_NaN();
    if (!b) cout << "Non-valid" << endl;
    else cout << 3/0 << endl;
    return 0;
}