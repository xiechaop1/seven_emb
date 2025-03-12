#include <iostream>
#include <vector>
#include <set>
#include <string>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <iterator>

using namespace std;

bool is_valid(const string &expression) {
    try {
        if (expression.find("/0") != string::npos) return false; // 避免除以零
        return true;
    } catch (...) {
        return false;
    }
}

double evaluate_expression(const string &expression) {
    try {
        istringstream iss(expression);
        vector<string> tokens((istream_iterator<string>(iss)), istream_iterator<string>());
        double result = stod(tokens[0]);
        for (size_t i = 1; i < tokens.size(); i += 2) {
            string op = tokens[i];
            double num = stod(tokens[i + 1]);
            if (op == "+") result += num;
            else if (op == "-") result -= num;
            else if (op == "*") result *= num;
            else if (op == "/" && num != 0) result /= num;
            else return 1e9;
        }
        return result;
    } catch (...) {
        return 1e9;
    }
}

string find_max_min_average(string expression) {
    vector<int> missing_positions;
    for (size_t i = 0; i < expression.size(); ++i) {
        if (expression[i] == '*') missing_positions.push_back(i);
    }
    string possible_replacements = "09+-*/";
    set<double> possible_values;
    
    size_t num_missing = missing_positions.size();
    size_t total_cases = pow(possible_replacements.size(), num_missing);
    
    for (size_t case_idx = 0; case_idx < total_cases; ++case_idx) {
        string new_expr = expression;
        size_t temp = case_idx;
        for (size_t j = 0; j < num_missing; ++j) {
            new_expr[missing_positions[j]] = possible_replacements[temp % possible_replacements.size()];
            temp /= possible_replacements.size();
        }
        if (is_valid(new_expr)) {
            double value = evaluate_expression(new_expr);
            if (value != 1e9) possible_values.insert(value);
        }
    }
    
    if (!possible_values.empty()) {
        double max_val = *max_element(possible_values.begin(), possible_values.end());
        double min_val = *min_element(possible_values.begin(), possible_values.end());
        double avg_val = (max_val + min_val) / 2;
        stringstream ss;
        ss << fixed << setprecision(2) << avg_val;
        return ss.str();
    }
    return "0.00";
}

int main() {
    string expr;
    cin >> expr;
    cout << find_max_min_average(expr) << endl;
    return 0;
}

