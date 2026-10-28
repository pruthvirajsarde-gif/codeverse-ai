import json
from flask import Blueprint, request, jsonify, Response, stream_with_context
from config import Config
from services.ai_service import AIService
from services.compiler_service import CompilerService
from services.offline_engine import VIVA_QUESTIONS, KNOWLEDGE_BASE

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/status", methods=["GET"])
def get_system_status():
    """Returns application status, AI provider config, and C++ compiler diagnostic details."""
    ai_status = AIService.get_provider_status()
    compiler_status = CompilerService.get_status()

    return jsonify({
        "status": "online",
        "app_name": Config.SYSTEM_NAME,
        "tagline": Config.TAGLINE,
        "ai": ai_status,
        "compiler": compiler_status,
        "version": "1.0.0",
        "supported_cpp_standards": ["C++98", "C++03", "C++11", "C++14", "C++17", "C++20", "C++23"]
    })

@api_bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    """Streams C++ mentor responses using Server-Sent Events (SSE)."""
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not messages:
        return jsonify({"error": "No messages provided."}), 400

    def generate():
        for chunk in AIService.stream_chat(messages):
            yield f"data: {chunk}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )

@api_bp.route("/execute", methods=["POST"])
def execute_code():
    """
    Executes C++ code through sandboxed compiler.
    Strictly follows requirement:
    'The Run Code button must genuinely compile and execute C++ code through a secure backend or trusted code-execution service. Do not simulate execution or display fabricated output. If code execution is not configured, show “Code execution is not configured yet” and explain how to enable it.'
    """
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    stdin_data = data.get("stdin", "")

    result = CompilerService.execute_cpp(code, stdin_data)
    return jsonify(result)

@api_bp.route("/learning-lab/concepts", methods=["GET"])
def get_concepts():
    """Returns categorized C++ concepts for the Concept Explorer."""
    concepts = [
        {
            "id": "intro",
            "level": "Beginner",
            "category": "Foundations",
            "title": "Basic Structure & I/O",
            "summary": "Understanding `#include <iostream>`, `main()`, `std::cout`, `std::cin`, and namespaces.",
            "code": "#include <iostream>\n\nint main() {\n    std::cout << \"Welcome to C++!\\n\";\n    return 0;\n}",
            "tags": ["Syntax", "cin/cout", "Basics"]
        },
        {
            "id": "variables-types",
            "level": "Beginner",
            "category": "Foundations",
            "title": "Data Types & Modifiers",
            "summary": "Fundamental types (int, float, double, char, bool), type sizes, signed vs unsigned, and `auto` type deduction.",
            "code": "#include <iostream>\n\nint main() {\n    int age = 21;\n    double gpa = 3.92;\n    char grade = 'A';\n    bool enrolled = true;\n    auto count = 500ULL;\n    std::cout << \"Age: \" << age << \", Size: \" << sizeof(count) << \" bytes\\n\";\n    return 0;\n}",
            "tags": ["Data Types", "auto", "sizeof"]
        },
        {
            "id": "pointers-refs",
            "level": "Intermediate",
            "category": "Memory",
            "title": "Pointers vs References",
            "summary": "Memory addresses, dereferencing `*`, address-of `&`, pass-by-reference, and pointer arithmetic.",
            "code": "#include <iostream>\n\nvoid swap(int& a, int& b) {\n    int temp = a;\n    a = b;\n    b = temp;\n}\n\nint main() {\n    int x = 10, y = 20;\n    swap(x, y);\n    std::cout << \"x: \" << x << \", y: \" << y << \"\\n\";\n    return 0;\n}",
            "tags": ["Pointers", "References", "Memory"]
        },
        {
            "id": "oop-classes",
            "level": "Intermediate",
            "category": "OOP",
            "title": "Classes & Encapsulation",
            "summary": "Access specifiers (public, private, protected), constructors, member initializers, and destructors.",
            "code": "#include <iostream>\n#include <string>\n\nclass BankAccount {\nprivate:\n    double balance;\npublic:\n    BankAccount(double init) : balance(init) {}\n    void deposit(double amt) { balance += amt; }\n    double getBalance() const { return balance; }\n};\n\nint main() {\n    BankAccount acc(100.0);\n    acc.deposit(50.0);\n    std::cout << \"Balance: $\" << acc.getBalance() << \"\\n\";\n    return 0;\n}",
            "tags": ["OOP", "Classes", "Encapsulation"]
        },
        {
            "id": "polymorphism",
            "level": "Intermediate",
            "category": "OOP",
            "title": "Virtual Functions & Polymorphism",
            "summary": "Dynamic dispatch, vtables, pure virtual methods (`= 0`), abstract classes, and the `override` keyword.",
            "code": "#include <iostream>\n\nclass Base {\npublic:\n    virtual void greet() const { std::cout << \"Hello from Base\\n\"; }\n    virtual ~Base() = default;\n};\n\nclass Derived : public Base {\npublic:\n    void greet() const override { std::cout << \"Hello from Derived\\n\"; }\n};\n\nint main() {\n    Base* ptr = new Derived();\n    ptr->greet();\n    delete ptr;\n    return 0;\n}",
            "tags": ["Polymorphism", "Virtual", "VTable"]
        },
        {
            "id": "stl-vectors",
            "level": "Intermediate",
            "category": "STL",
            "title": "STL Vector & Algorithms",
            "summary": "Contiguous dynamic arrays, iterators, `std::sort`, `std::binary_search`, and amortized O(1) appending.",
            "code": "#include <iostream>\n#include <vector>\n#include <algorithm>\n\nint main() {\n    std::vector<int> v = {40, 10, 30, 20};\n    v.push_back(50);\n    std::sort(v.begin(), v.end());\n    for (int n : v) std::cout << n << \" \";\n    std::cout << \"\\n\";\n    return 0;\n}",
            "tags": ["STL", "Vector", "Algorithms"]
        },
        {
            "id": "smart-pointers",
            "level": "Advanced",
            "category": "Modern C++",
            "title": "Smart Pointers & RAII",
            "summary": "Automatic memory lifecycle management with `std::unique_ptr`, `std::shared_ptr`, and `std::weak_ptr`.",
            "code": "#include <iostream>\n#include <memory>\n\nstruct Node {\n    int val;\n    Node(int v) : val(v) { std::cout << \"Node(\" << val << \") created\\n\"; }\n    ~Node() { std::cout << \"Node(\" << val << \") destroyed\\n\"; }\n};\n\nint main() {\n    auto node = std::make_unique<Node>(42);\n    std::cout << \"Value: \" << node->val << \"\\n\";\n    return 0;\n}",
            "tags": ["Modern C++", "Smart Pointers", "RAII"]
        },
        {
            "id": "templates",
            "level": "Advanced",
            "category": "Generic Programming",
            "title": "Templates & Metaprogramming",
            "summary": "Function and class templates, template specialization, `typename`, and compile-time type safety.",
            "code": "#include <iostream>\n\ntemplate <typename T>\nT getMax(T a, T b) {\n    return (a > b) ? a : b;\n}\n\nint main() {\n    std::cout << getMax<int>(10, 25) << \"\\n\";\n    std::cout << getMax<double>(3.14, 2.71) << \"\\n\";\n    return 0;\n}",
            "tags": ["Templates", "Generics", "Compile-Time"]
        },
        {
            "id": "move-semantics",
            "level": "Advanced",
            "category": "Modern C++",
            "title": "Move Semantics & R-values",
            "summary": "R-value references `&&`, `std::move`, Move Constructors, and avoiding deep copies for expensive objects.",
            "code": "#include <iostream>\n#include <vector>\n#include <utility>\n\nint main() {\n    std::vector<int> a = {1, 2, 3, 4, 5};\n    std::vector<int> b = std::move(a); // Transfers buffer ownership, O(1) cost\n    std::cout << \"a size: \" << a.size() << \", b size: \" << b.size() << \"\\n\";\n    return 0;\n}",
            "tags": ["Move Semantics", "R-Value", "Performance"]
        }
    ]
    return jsonify({"concepts": concepts})

@api_bp.route("/learning-lab/quiz", methods=["GET"])
def get_quiz():
    """Returns curated C++ MCQs for interactive testing with explanations."""
    quiz_questions = [
        {
            "id": 1,
            "category": "Pointers",
            "difficulty": "Easy",
            "question": "What will be printed by the following code?\nint x = 10;\nint* p = &x;\n*p = 25;\nstd::cout << x;",
            "options": ["10", "25", "Memory Address of x", "Compilation Error"],
            "correct": 1,
            "explanation": "`*p = 25` dereferences pointer `p` (which holds `&x`) and overwrites the value stored at `x`'s memory location with 25."
        },
        {
            "id": 2,
            "category": "OOP",
            "difficulty": "Medium",
            "question": "Which of the following operators CANNOT be overloaded in C++?",
            "options": ["+", "[]", "::", "=="],
            "correct": 2,
            "explanation": "The Scope Resolution Operator (`::`), Member Selection (`.`), Pointer to Member (`.*`), Ternary (`?:`), and `sizeof` cannot be overloaded in C++."
        },
        {
            "id": 3,
            "category": "Memory",
            "difficulty": "Medium",
            "question": "What is the key difference between delete and delete[] in C++?",
            "options": [
                "delete is for primitive types; delete[] is for objects.",
                "delete calls one destructor; delete[] calls destructors for every element in an array.",
                "There is no difference; compilers treat them identically.",
                "delete[] also zeroes the pointer memory."
            ],
            "correct": 1,
            "explanation": "`delete[]` looks up the array allocation metadata to invoke destructors for each element in the allocated buffer before freeing the block."
        },
        {
            "id": 4,
            "category": "Modern C++",
            "difficulty": "Hard",
            "question": "Which smart pointer does NOT allow multiple owners of the same resource?",
            "options": ["std::shared_ptr", "std::weak_ptr", "std::unique_ptr", "std::auto_ptr"],
            "correct": 2,
            "explanation": "`std::unique_ptr` implements strict exclusive ownership semantics. Copying is disabled (`= delete`), and ownership can only be transferred via `std::move`."
        },
        {
            "id": 5,
            "category": "STL",
            "difficulty": "Medium",
            "question": "What is the worst-case time complexity of searching an element in std::unordered_map?",
            "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
            "correct": 2,
            "explanation": "`std::unordered_map` has an average time complexity of O(1), but in the worst case (when multiple hash collisions occur and all elements fall into the same bucket), searching degrades to O(N)."
        },
        {
            "id": 6,
            "category": "Inheritance",
            "difficulty": "Hard",
            "question": "How do you solve the Diamond Problem in multiple inheritance in C++?",
            "options": [
                "By declaring methods as static",
                "By using virtual inheritance (e.g. `class B : virtual public A`)",
                "By making the base class final",
                "By declaring all variables private"
            ],
            "correct": 1,
            "explanation": "Virtual inheritance ensures that only one shared instance of the common base class subobject is included in the most derived class, resolving ambiguity."
        }
    ]
    return jsonify({"questions": quiz_questions})

@api_bp.route("/learning-lab/viva", methods=["GET"])
def get_viva_questions():
    """Returns curated C++ college viva practical examination Q&A."""
    return jsonify({"viva": VIVA_QUESTIONS})

@api_bp.route("/learning-lab/challenge", methods=["GET"])
def get_daily_challenge():
    """Returns the featured C++ Daily Coding Challenge."""
    challenge = {
        "title": "Reverse a Singly Linked List (Iterative & Recursive)",
        "difficulty": "Medium",
        "description": "Given the pointer to the `head` node of a singly linked list, reverse the list in-place and return the new head pointer.",
        "starter_code": """#include <iostream>

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(nullptr) {}
};

ListNode* reverseList(ListNode* head) {
    // TODO: Write iterative O(N) time and O(1) space solution
    ListNode* prev = nullptr;
    ListNode* curr = head;
    while (curr != nullptr) {
        ListNode* nextTemp = curr->next;
        curr->next = prev;
        prev = curr;
        curr = nextTemp;
    }
    return prev;
}

int main() {
    ListNode* head = new ListNode(1);
    head->next = new ListNode(2);
    head->next->next = new ListNode(3);

    ListNode* rev = reverseList(head);
    std::cout << "Reversed Head Value: " << rev->val << std::endl;
    return 0;
}""",
        "hints": [
            "Use three pointers: `prev` (initialized to `nullptr`), `curr` (initialized to `head`), and `nextTemp`.",
            "In each step, save `curr->next`, point `curr->next = prev`, shift `prev = curr`, and advance `curr = nextTemp`.",
            "Time Complexity should be O(N) with O(1) auxiliary space."
        ],
        "solution_explanation": "The iterative three-pointer technique reverses links one by one without allocating additional nodes on the heap, ensuring O(N) time complexity and O(1) space complexity."
    }
    return jsonify({"challenge": challenge})

@api_bp.route("/learning-lab/cheatsheet", methods=["GET"])
def get_cheatsheet():
    """Returns fast syntax, STL tables, and reference cards."""
    cheatsheet = {
        "io_manipulators": [
            {"syntax": "std::fixed << std::setprecision(2)", "header": "<iomanip>", "desc": "Format floating points to 2 decimal places"},
            {"syntax": "std::setw(10) << std::setfill('0')", "header": "<iomanip>", "desc": "Pad output with leading zeroes"},
            {"syntax": "std::boolalpha", "header": "<iostream>", "desc": "Print booleans as 'true'/'false' instead of 1/0"}
        ],
        "stl_containers": [
            {"container": "std::vector<T>", "underlying": "Dynamic Array", "access": "O(1)", "insert_back": "O(1) amortized", "header": "<vector>"},
            {"container": "std::deque<T>", "underlying": "Chunked Array", "access": "O(1)", "insert_back": "O(1) front & back", "header": "<deque>"},
            {"container": "std::list<T>", "underlying": "Doubly Linked List", "access": "O(N)", "insert_back": "O(1)", "header": "<list>"},
            {"container": "std::set<T>", "underlying": "Red-Black Tree", "access": "O(log N)", "insert_back": "O(log N)", "header": "<set>"},
            {"container": "std::unordered_map<K, V>", "underlying": "Hash Table", "access": "O(1) avg", "insert_back": "O(1) avg", "header": "<unordered_map>"},
            {"container": "std::priority_queue<T>", "underlying": "Max Heap", "access": "O(1) top", "insert_back": "O(log N) push", "header": "<queue>"}
        ],
        "keywords": [
            {"keyword": "constexpr", "standard": "C++11/14", "desc": "Constant expression evaluated at compile time for zero runtime overhead."},
            {"keyword": "explicit", "standard": "C++98", "desc": "Prevents the compiler from applying implicit conversion or copy-initialization."},
            {"keyword": "noexcept", "standard": "C++11", "desc": "Declares that a function guarantees not to throw any exceptions, enabling compiler optimizations."},
            {"keyword": "nullptr", "standard": "C++11", "desc": "Type-safe null pointer literal of type std::nullptr_t, replacing ambiguous 0 / NULL."}
        ]
    }
    return jsonify({"cheatsheet": cheatsheet})
