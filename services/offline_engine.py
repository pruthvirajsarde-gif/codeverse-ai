"""
CodeVerse AI - Intelligent Offline C++ Knowledge & Reasoning Engine
Provides robust, structured C++ educational responses, strictly enforcing the C++ only domain rule.
Differentiates intelligently between Theory requests, Code requests, and balanced conceptual masterclasses.
"""

import re
from typing import Dict, Any, Optional

OUT_OF_SCOPE_REFUSAL = (
    "I’m CodeVerse AI, your dedicated C++ programming assistant! 💻 "
    "I can help you with C++ concepts, programs, debugging, algorithms, and output prediction. "
    "Please ask me a C++-related question, and let’s code together!"
)

# Non-C++ topics detection patterns
NON_CPP_PATTERNS = [
    r"\b(cricket|football|soccer|tennis|messi|ronaldo|ipl|nba)\b",
    r"\b(politics|president|prime minister|election|government|bjp|congress|democrat|republican)\b",
    r"\b(weather|temperature|forecast|rain|climate)\b",
    r"\b(recipe|cake|cooking|pasta|pizza|biryani|burger)\b",
    r"\b(movie|cinema|actor|actress|hollywood|bollywood|netflix)\b",
    r"\b(relationship|dating|love advice|breakup|horoscope|zodiac)\b",
    r"\b(crypto|bitcoin|stock market|forex|investing)\b",
    r"\b(python|java|javascript|php|ruby|swift|kotlin|c#|rust|golang|html|css)\b(?!\s+(vs|versus|difference|compared|to C\+\+|to c\+\+))",
]

# Rich Curated C++ Knowledge Base with dedicated Theory, Diagrams, Code, and Complexity
KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "pointer": {
        "title": "Pointers and Memory Addresses in C++",
        "definition": "A **pointer** in C++ is a compound type variable that stores the direct physical or virtual byte address of another object in computer memory (RAM).",
        "theory": (
            "In von Neumann computer architecture, system memory is organized as a sequential array of 1-byte storage cells, each possessing a hexadecimal address.\n\n"
            "**Core Theoretical Pillars:**\n"
            "1. **Direct Memory Mapping:** Instead of operating on variable values, pointers allow direct manipulation of physical RAM, bypassing abstraction layers for maximum performance.\n"
            "2. **Address-of Operator (`&`):** Evaluates to the memory location of an lvalue operand.\n"
            "3. **Dereference Operator (`*`):** Indirection operator that reads or writes the memory cell stored in the pointer.\n"
            "4. **Pointer Arithmetic:** Stepping a pointer (`ptr + 1`) increments the address by `sizeof(T)` bytes, allowing fast contiguous buffer traversal.\n"
            "5. **Pointer Types & Sizing:** On 64-bit architectures, every pointer is strictly 8 bytes (64 bits), regardless of whether it points to a 1-byte `char` or a 1000-byte `struct`."
        ),
        "diagram": (
            "```text\n"
            "+---------------+           +-------------------+\n"
            "| Variable: ptr |           |  Variable: score  |\n"
            "| Address: 0x70 | --------> |  Address: 0x54    |\n"
            "| Value: 0x54   |           |  Value: 95        |\n"
            "+---------------+           +-------------------+\n"
            "```"
        ),
        "mechanism": (
            "- **Stack Frame Allocation:** Local variables are assigned addresses by the compiler offset relative to the stack pointer register (RSP/ESP).\n"
            "- **Indirection Cycle:** When `*ptr` is evaluated, the CPU loads the address from `ptr` into an address register and performs a second memory bus cycle to fetch the target value."
        ),
        "tradeoffs": (
            "- **Advantages:** Zero-cost parameter passing, dynamic polymorphism, efficient heap resource management, enabling high-performance data structures (linked lists, trees, graphs).\n"
            "- **Trade-Offs:** Manual lifecycle liability, susceptibility to dangling pointers, memory leaks, buffer overflows, and cache misses from pointer chasing."
        ),
        "viva": (
            "- **Q:** What is the size of a pointer in 64-bit C++?\n"
            "  **A:** Exactly 8 bytes on 64-bit systems, regardless of data type.\n"
            "- **Q:** What is the difference between `nullptr` and `NULL`?\n"
            "  **A:** `nullptr` (C++11) is a type-safe literal of type `std::nullptr_t`. `NULL` is a preprocessor macro defined as integral `0` or `(void*)0` causing ambiguity in function overloading."
        ),
        "code": """#include <iostream>

int main() {
    int score = 95;
    int* ptr = &score; // ptr holds memory address of score

    std::cout << "Direct value of score: " << score << std::endl;
    std::cout << "Address of score (&score): " << &score << std::endl;
    std::cout << "Value stored in pointer (ptr): " << ptr << std::endl;
    std::cout << "Dereferenced pointer (*ptr): " << *ptr << std::endl;

    // Modifying target value through pointer indirection
    *ptr = 100;
    std::cout << "Updated score via pointer indirection: " << score << std::endl;

    return 0;
}""",
        "output": """Direct value of score: 95
Address of score (&score): 0x7ffd98b44a3c
Value stored in pointer (ptr): 0x7ffd98b44a3c
Dereferenced pointer (*ptr): 95
Updated score via pointer indirection: 100""",
        "breakdown": (
            "1. `int score = 95;` reserves 4 bytes on stack memory.\n"
            "2. `int* ptr = &score;` allocates an 8-byte pointer holding the stack address `&score`.\n"
            "3. `*ptr = 100;` dereferences the pointer, performing a memory store operation at `&score`.\n"
            "4. Verifies that `score` was modified in-place without copying."
        ),
        "complexity": "Time Complexity: O(1) for address resolution and dereference. Space Complexity: 8 bytes on 64-bit architecture.",
        "pitfalls": (
            "- **Wild Pointers:** Declaring `int* p;` without initialization points to arbitrary memory.\n"
            "- **Dangling Pointers:** Accessing memory after calling `delete p`.\n"
            "- **Memory Leaks:** Allocating with `new` without a matching `delete`."
        ),
        "practice": "Write a C++ function `void swap(int* a, int* b)` using pointer dereferencing to swap two integers without temporary variables."
    },

    "constructor": {
        "title": "Constructors, Destructors and RAII in C++",
        "definition": "A **constructor** is a non-static member function that initializes newly created objects of a class. A **destructor** is a special member function that cleans up resources when an object's lifetime ends.",
        "theory": (
            "In C++, constructors and destructors form the foundation of **RAII (Resource Acquisition Is Initialization)**.\n\n"
            "**Core Theoretical Concepts:**\n"
            "1. **Automatic Invocation:** The compiler guarantees constructor execution upon object instantiation (stack allocation or `new`), and guarantees destructor execution when the object exits its enclosing scope or is deleted.\n"
            "2. **Member Initializer List:** Syntax `: member1(arg1), member2(arg2)` initializes fields *before* the constructor body runs, preventing redundant default construction followed by copy assignment.\n"
            "3. **Special Member Functions (Rule of 0/3/5):**\n"
            "   - Default Constructor (`T()`)\n"
            "   - Copy Constructor (`T(const T&)`)\n"
            "   - Move Constructor (`T(T&&)` in C++11)\n"
            "   - Copy Assignment (`T& operator=(const T&)`)\n"
            "   - Move Assignment (`T& operator=(T&&)`)\n"
            "   - Destructor (`~T()`)\n"
            "4. **Virtual Destructors:** When deleting an object through a base pointer (`Base* b = new Derived()`), the base class destructor **MUST** be declared `virtual` to prevent undefined behavior and memory leaks."
        ),
        "diagram": (
            "```text\n"
            "[Scope Enters] ---> Constructor Runs ---> Object Valid in Memory\n"
            "                                             |\n"
            "[Scope Exits]  <--- Destructor Runs  <-------+\n"
            "```"
        ),
        "mechanism": (
            "- Upon object creation, stack space is allocated, the class vptr is initialized (if virtual methods exist), base constructors run in inheritance order, and members initialize in declaration order.\n"
            "- Destructors run in reverse order of construction, releasing heap buffers, locks, or file handles."
        ),
        "tradeoffs": (
            "- **Advantages:** Eliminates manual cleanup code, guarantees exception safety, prevents resource leaks.\n"
            "- **Trade-Offs:** Complex order-of-initialization dependencies when base classes or static objects are involved."
        ),
        "viva": (
            "- **Q:** Can constructors be virtual in C++?\n"
            "  **A:** No, because an object's vtable pointer (`vptr`) does not exist until the constructor initializes it.\n"
            "- **Q:** Why should base class destructors be virtual?\n"
            "  **A:** To ensure that `delete basePtr` invokes the derived destructor first, properly releasing derived resources."
        ),
        "code": """#include <iostream>
#include <string>

class Session {
private:
    std::string user;
    int* buffer;

public:
    // Parameterized Constructor using Member Initializer List
    Session(const std::string& username, int bufferSize) 
        : user(username), buffer(new int[bufferSize]) {
        std::cout << "[Constructor] Session created for " << user << std::endl;
    }

    void process() {
        std::cout << "[Action] Session active for " << user << std::endl;
    }

    // Destructor (Guaranteed cleanup via RAII)
    ~Session() {
        delete[] buffer; // Deallocate heap memory safely
        std::cout << "[Destructor] Session destroyed and memory freed for " << user << std::endl;
    }
};

int main() {
    {
        Session s1("Alice", 1024);
        s1.process();
    } // s1 goes out of scope here: ~Session() runs automatically!

    std::cout << "[Main] Exited scope safely." << std::endl;
    return 0;
}""",
        "output": """[Constructor] Session created for Alice
[Action] Session active for Alice
[Destructor] Session destroyed and memory freed for Alice
[Main] Exited scope safely.""",
        "breakdown": (
            "1. Member initializer `: user(username), buffer(new int[bufferSize])` directly constructs fields in-place.\n"
            "2. When execution leaves the inner `{ }` scope, the compiler automatically invokes `~Session()`.\n"
            "3. `delete[] buffer;` ensures heap allocated integers are deallocated without manual tracking."
        ),
        "complexity": "Time Complexity: O(1) instantiation and destruction. Space Complexity: O(N) dynamic buffer on the heap.",
        "pitfalls": (
            "- Shallow copying with raw pointers: If an object is copied without a user-defined copy constructor, two objects will point to the same buffer, causing a **Double Free** crash.\n"
            "- Throwing exceptions from destructors is forbidden (`noexcept` by default in C++11)."
        ),
        "practice": "Implement the Rule of Five for a class managing a dynamically allocated integer array."
    },

    "inheritance": {
        "title": "Inheritance, Polymorphism & Virtual Tables in C++",
        "definition": "Inheritance is an OOP mechanism allowing a derived class to acquire properties and methods of a base class. Polymorphism allows derived types to be treated through common base interfaces with dynamic runtime dispatch.",
        "theory": (
            "C++ supports both **compile-time polymorphism** (templates, function overloading) and **runtime polymorphism** (virtual functions).\n\n"
            "**Key Theoretical Principles:**\n"
            "1. **Access Specifiers in Inheritance:**\n"
            "   - `public`: `public` remains `public`, `protected` remains `protected`.\n"
            "   - `protected`: `public` becomes `protected` in derived class.\n"
            "   - `private`: all inherited members become `private`.\n"
            "2. **Dynamic Dispatch & VTable:** When a class declares a `virtual` function, the compiler inserts a hidden pointer (`__vptr`) into every object instance pointing to a static Virtual Method Table (`vtable`) of function pointers.\n"
            "3. **Pure Virtual Functions & Abstract Classes:** Declaring a method as `= 0` makes the class abstract, meaning it cannot be instantiated directly.\n"
            "4. **Diamond Problem:** In multiple inheritance (`B` and `C` inherit from `A`, and `D` inherits from `B` and `C`), `D` contains two duplicate subobjects of `A`. Solved via `virtual public A`."
        ),
        "diagram": (
            "```text\n"
            "    [Base Class: Shape] (vptr -> Shape VTable)\n"
            "           ^\n"
            "           | public inheritance\n"
            "    [Derived: Circle]   (vptr -> Circle VTable -> Circle::draw)\n"
            "```"
        ),
        "mechanism": (
            "- Base class constructor executes first, followed by derived class constructor.\n"
            "- Virtual function calls through pointers resolve at runtime: `objPtr->__vptr[index]()` incurring a single memory dereference overhead."
        ),
        "tradeoffs": (
            "- **Advantages:** Code reusability, modular architecture, extensibility via interfaces.\n"
            "- **Trade-Offs:** Virtual function calls prevent compiler inlining, slight memory overhead (8-byte `vptr` per object)."
        ),
        "viva": (
            "- **Q:** How is runtime polymorphism implemented under the hood in C++?\n"
            "  **A:** Via Virtual Method Tables (`vtables`) containing function pointers, and a virtual table pointer (`vptr`) inside each object.\n"
            "- **Q:** What is an abstract class?\n"
            "  **A:** A class containing at least one pure virtual function (`virtual void f() = 0;`)."
        ),
        "code": """#include <iostream>
#include <vector>
#include <memory>

// Abstract Base Class / Interface
class Animal {
public:
    virtual void speak() const = 0; // Pure virtual function
    virtual ~Animal() = default;    // Essential virtual destructor
};

class Dog : public Animal {
public:
    void speak() const override {
        std::cout << "Dog barks: Woof! Woof!" << std::endl;
    }
};

class Cat : public Animal {
public:
    void speak() const override {
        std::cout << "Cat meows: Meow! Purr!" << std::endl;
    }
};

int main() {
    // Polymorphic collection using modern unique_ptr
    std::vector<std::unique_ptr<Animal>> pets;
    pets.push_back(std::make_unique<Dog>());
    pets.push_back(std::make_unique<Cat>());

    for (const auto& pet : pets) {
        pet->speak(); // Dynamic dispatch at runtime via vtable
    }

    return 0;
}""",
        "output": """Dog barks: Woof! Woof!
Cat meows: Meow! Purr!""",
        "breakdown": (
            "1. `Animal` is an abstract interface with pure virtual `speak() = 0`.\n"
            "2. `Dog` and `Cat` implement `speak()` using the `override` keyword.\n"
            "3. Iterating through `pet->speak()` dynamically resolves to the derived class implementation via the vtable."
        ),
        "complexity": "Time Complexity: O(1) for virtual dispatch (one table lookup). Space: 8 bytes per object for vptr.",
        "pitfalls": (
            "- Forgetting `virtual ~Base()` leads to derived destructor not being called when deleted through a base pointer.\n"
            "- Object slicing: Assigning a derived object to a base value variable strips the derived data."
        ),
        "practice": "Write code demonstrating virtual inheritance to resolve the Diamond Problem."
    },

    "vector": {
        "title": "C++ STL std::vector Dynamic Array & Memory Reallocation",
        "definition": "`std::vector` is a sequence container in `<vector>` that encapsulates a dynamically resizable, contiguous memory array.",
        "theory": (
            "`std::vector` provides the random access speed of C arrays while eliminating fixed compile-time size limitations.\n\n"
            "**Core Memory Mechanics:**\n"
            "1. **Three Internal Pointers:** An STL vector typically contains 3 raw pointers: `_Myfirst` (start of storage), `_Mylast` (end of valid elements), and `_Myend` (end of allocated capacity).\n"
            "2. **Size vs Capacity:**\n"
            "   - `size()`: Number of currently stored active elements.\n"
            "   - `capacity()`: Maximum elements storable before reallocation is required.\n"
            "3. **Geometric Reallocation:** When `size() == capacity()` and a new element is inserted, vector allocates a new memory block (typically 1.5x or 2x size), moves/copies existing items, and deallocates the old buffer.\n"
            "4. **Amortized O(1) Complexity:** Although a single reallocation takes O(N) time, the doubling strategy ensures that N insertions take O(N) total work, resulting in an average O(1) time per insertion."
        ),
        "diagram": (
            "```text\n"
            "Allocated Heap Buffer (Capacity = 4):\n"
            "[ 10 | 20 | 30 | empty ]\n"
            "  ^              ^         ^\n"
            "  start          size      capacity\n"
            "```"
        ),
        "mechanism": (
            "- Elements are guaranteed to be stored contiguously in memory, yielding superior CPU cache locality compared to linked lists.\n"
            "- `shrink_to_fit()` requests the removal of unused capacity."
        ),
        "tradeoffs": (
            "- **Advantages:** O(1) random access, fast back insertions, cache friendly.\n"
            "- **Trade-Offs:** O(N) insertion/deletion at front or middle, reallocation invalidates iterators."
        ),
        "viva": (
            "- **Q:** What is iterator invalidation in `std::vector`?\n"
            "  **A:** When `push_back()` triggers buffer reallocation, all pointers, references, and iterators to previous elements become invalid and dangling."
        ),
        "code": """#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> vec = {10, 20, 30};

    std::cout << "Initial size: " << vec.size() << ", capacity: " << vec.capacity() << std::endl;

    vec.push_back(40);
    vec.push_back(50); // Triggers capacity expansion

    std::cout << "After expansion size: " << vec.size() << ", capacity: " << vec.capacity() << std::endl;

    // Sorting with standard algorithm
    std::sort(vec.begin(), vec.end(), std::greater<int>());

    std::cout << "Elements in descending order: ";
    for (int num : vec) {
        std::cout << num << " ";
    }
    std::cout << std::endl;

    return 0;
}""",
        "output": """Initial size: 3, capacity: 3
After expansion size: 5, capacity: 6
Elements in descending order: 50 40 30 20 10""",
        "breakdown": (
            "1. Vector initialized with 3 elements (size 3, capacity 3).\n"
            "2. Appending elements triggers heap reallocation, doubling capacity to 6.\n"
            "3. `std::sort` executes in O(N log N) using IntroSort."
        ),
        "complexity": "Random Access: O(1). Append (push_back): O(1) amortized. Insert/Delete at middle: O(N).",
        "pitfalls": (
            "- Accessing out-of-bounds index via `vec[i]` causes undefined behavior. Use `vec.at(i)` for bounds-checked exception safety."
        ),
        "practice": "Why is `std::vector<bool>` considered a specialized non-standard container in C++?"
    },

    "binary_search": {
        "title": "Binary Search Algorithm in C++",
        "definition": "Binary Search is an efficient divide-and-conquer search algorithm that determines the position of a target key in a **monotonically sorted** contiguous sequence in logarithmic time.",
        "theory": (
            "Instead of sequentially scanning through N items (O(N) linear search), Binary Search repeatedly divides the search interval in half.\n\n"
            "**Theoretical Foundation:**\n"
            "1. **Monotonicity Requirement:** The dataset MUST be sorted beforehand (ascending or descending).\n"
            "2. **Divide-and-Conquer Recurrence:** $T(N) = T(N/2) + O(1)$, which resolves to $O(\\log_2 N)$ by the Master Theorem.\n"
            "3. **Integer Overflow Guard:** Computing midpoint as `mid = (low + high) / 2` risks 32-bit signed integer overflow when `low + high > 2,147,483,647`. The correct formulation is `mid = low + (high - low) / 2`.\n"
            "4. **STL Equivalents:** C++ provides `std::binary_search` (returns bool), `std::lower_bound` (first element $\\ge$ key), and `std::upper_bound` (first element $>$ key)."
        ),
        "diagram": (
            "```text\n"
            "Step 1: [ 3 | 9 | 14 | 19 | 25 | 31 | 42 | 55 | 68 ] Target = 42\n"
            "          ^                   ^                   ^\n"
            "         low                 mid                 high\n"
            "Step 2: 42 > 25 -> search right half [ 31 | 42 | 55 | 68 ]\n"
            "```"
        ),
        "mechanism": (
            "- Compares target with midpoint element.\n"
            "- If matched, returns index immediately.\n"
            "- If target is smaller, eliminates the right half by setting `high = mid - 1`.\n"
            "- If target is larger, eliminates the left half by setting `low = mid + 1`."
        ),
        "tradeoffs": (
            "- **Advantages:** Extremely fast (search 1,000,000 elements in at most 20 comparisons).\n"
            "- **Trade-Offs:** Requires pre-sorted data ($O(N \\log N)$ sorting cost if unsorted)."
        ),
        "viva": (
            "- **Q:** How many maximum comparisons does binary search take for 1,024 elements?\n"
            "  **A:** $\\log_2(1024) = 10$ comparisons."
        ),
        "code": """#include <iostream>
#include <vector>

int binarySearch(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = static_cast<int>(arr.size()) - 1;

    while (low <= high) {
        // Safe midpoint calculation avoiding integer overflow
        int mid = low + (high - low) / 2;

        if (arr[mid] == target) {
            return mid; // Target found
        } else if (arr[mid] < target) {
            low = mid + 1; // Discard left half
        } else {
            high = mid - 1; // Discard right half
        }
    }
    return -1; // Target not found
}

int main() {
    std::vector<int> sortedData = {4, 8, 15, 16, 23, 42, 58, 77, 91};
    int target = 42;

    int index = binarySearch(sortedData, target);

    if (index != -1) {
        std::cout << "Target element " << target << " found at index: " << index << std::endl;
    } else {
        std::cout << "Target element not found." << std::endl;
    }

    return 0;
}""",
        "output": "Target element 42 found at index: 5",
        "breakdown": (
            "1. Search interval begins across full array bounds `[0, size - 1]`.\n"
            "2. Overflow-safe `mid = low + (high - low) / 2` calculates midpoint.\n"
            "3. Bounds adjust conditionally until target matches or interval is exhausted."
        ),
        "complexity": "Time Complexity: Best Case O(1), Worst/Average Case O(log N). Auxiliary Space Complexity: O(1) iterative.",
        "pitfalls": (
            "- Running binary search on unsorted data.\n"
            "- Off-by-one errors in while condition: using `low < high` instead of `low <= high` can miss single-element matches."
        ),
        "practice": "How does `std::lower_bound` differ from `std::upper_bound` in C++ STL?"
    }
}

# C++ Viva Questions Database
VIVA_QUESTIONS = [
    {
        "q": "What is the difference between C and C++?",
        "a": "C is a procedural programming language developed by Dennis Ritchie, while C++ is a multi-paradigm language (supports procedural, object-oriented, and generic programming) created by Bjarne Stroustrup. C++ introduces classes, inheritance, polymorphism, templates, exception handling, and the Standard Template Library (STL)."
    },
    {
        "q": "What is the difference between `new`/`delete` and `malloc()`/`free()`?",
        "a": "`new` and `delete` are C++ operators that automatically call constructors and destructors, allocate memory type-safely, and return exact typed pointers. `malloc()` and `free()` are C library functions in `<cstdlib>` that allocate raw byte memory, return `void*`, require explicit casting, and DO NOT invoke object constructors or destructors."
    },
    {
        "q": "What is a virtual function and why is it used?",
        "a": "A virtual function is a member function in a base class declared with the `virtual` keyword that can be overridden in a derived class. It enables runtime polymorphism (dynamic binding) through a virtual method table (vtable). When invoked via a base pointer or reference, C++ calls the function of the actual derived object."
    },
    {
        "q": "What is an abstract class and pure virtual function?",
        "a": "A pure virtual function is a virtual function with `= 0` in its declaration (e.g., `virtual void draw() = 0;`). An abstract class is a class containing at least one pure virtual function. Abstract classes cannot be instantiated directly and serve as blueprints for derived classes."
    },
    {
        "q": "What is the difference between a pointer and a reference in C++?",
        "a": "1. Pointers can be reassigned to point to different memory locations; references cannot be rebound after initialization.\n2. Pointers can hold `nullptr`; references must refer to an existing valid object.\n3. Pointers have their own memory address; references act as aliases sharing the target's address.\n4. Pointers require dereferencing (`*p` or `->`); references use standard dot/variable syntax."
    },
    {
        "q": "What are Smart Pointers in C++11 and why should we use them?",
        "a": "Smart pointers (`std::unique_ptr`, `std::shared_ptr`, `std::weak_ptr`) manage object lifecycles automatically using RAII (Resource Acquisition Is Initialization). They automatically deallocate memory when going out of scope, preventing memory leaks, double free errors, and dangling pointers."
    },
    {
        "q": "What is the difference between `struct` and `class` in C++?",
        "a": "The only semantic difference in C++ is default access: members and base inheritance of a `struct` are `public` by default, whereas in a `class`, members and base inheritance are `private` by default. Both can have methods, constructors, and inheritance."
    },
    {
        "q": "What is operator overloading? Can all operators be overloaded?",
        "a": "Operator overloading allows standard C++ operators (+, -, *, <<, ==, etc.) to have customized behavior for user-defined classes. Not all operators can be overloaded: `::` (scope resolution), `.` (member access), `.*` (pointer to member), `?:` (ternary), and `sizeof` cannot be overloaded."
    }
]

class OfflineEngine:
    """Intelligent C++ offline reasoning and response generator."""

    @staticmethod
    def is_out_of_scope(query: str) -> bool:
        """Determines if the query is unrelated to C++ programming."""
        query_lower = query.lower().strip()

        # Check explicit non-cpp topics
        for pattern in NON_CPP_PATTERNS:
            if re.search(pattern, query_lower):
                cpp_indicators = ["c++", "cpp", "c plus plus", "cin", "cout", "pointer", "vector", "class", "stl", "code in c++", "program in c++"]
                has_cpp = any(ind in query_lower for ind in cpp_indicators)
                if not has_cpp:
                    return True

        return False

    @staticmethod
    def generate_response(query: str, history: Optional[list] = None) -> str:
        """
        Generates a structured, professional C++ tutor response.
        Intelligently detects:
        - Theory requests ("give theory", "explain theory", "what is", "notes on...")
        - Code requests ("give code", "generate code", "write a program", "code for...")
        - General/Mixed queries (balanced theory + code; NEVER code only!)
        """
        query_clean = query.strip()
        query_lower = query_clean.lower()

        # 1. Strict C++ boundary
        if OfflineEngine.is_out_of_scope(query_clean):
            return OUT_OF_SCOPE_REFUSAL

        # 2. Greeting / Introduction
        if any(query_lower.startswith(g) for g in ["hi", "hello", "hey", "who are you", "what can you do"]):
            return (
                "👋 **Greetings! I am CodeVerse AI**, your dedicated C++ Programming Mentor.\n\n"
                "I specialize exclusively in C++ concepts, programs, algorithms, data structures, and debugging. Here is how I can assist you:\n\n"
                "- 📘 **Theory & Concepts:** Ask *'Give theory of pointers'* or *'Explain virtual functions'* for in-depth theoretical analysis, memory diagrams, and principles.\n"
                "- 💻 **Code Generation:** Ask *'Give code for Binary Search'* or *'Write program for operator overloading'* for complete, compilable programs.\n"
                "- 🛠️ **Debug Code:** Pinpoint syntax errors, segmentation faults, memory leaks, and logical bugs.\n"
                "- 🔍 **Predict Output:** Step-by-step trace and dry-run analysis for C++ snippets.\n"
                "- 🎓 **Viva & Exam Prep:** Prepare college practical and interview questions.\n\n"
                "What C++ concept would you like to explore today?"
            )

        # 3. Detect User Intent (Theory vs Code vs Balanced)
        theory_triggers = [
            "theory", "explain theory", "give theory", "give me theory",
            "concept", "concepts", "notes", "principle", "principles",
            "mechanism", "architecture", "what is", "what are",
            "why do we", "how does", "difference between", "explain in detail", "explain"
        ]
        is_theory_intent = any(t in query_lower for t in theory_triggers)

        code_triggers = [
            "give code", "generate code", "write code", "program for", "code for",
            "implement", "solution code", "code of", "write a c++ program",
            "c++ program for", "show code", "give me code", "write a program",
            "code to", "just code", "only code", "source code"
        ]
        is_code_intent = any(c in query_lower for c in code_triggers)

        # 4. Viva questions query
        if "viva" in query_lower or "interview questions" in query_lower:
            return OfflineEngine._generate_viva_pack()

        # 5. Output prediction query
        if "predict" in query_lower or "output of" in query_lower or "what will be the output" in query_lower:
            return OfflineEngine._handle_output_prediction(query_clean)

        # 6. Debugging query
        if "debug" in query_lower or "fix" in query_lower or "segfault" in query_lower or ("error" in query_lower and "code" in query_lower):
            return OfflineEngine._handle_debugging(query_clean)

        # 7. Search curated knowledge base
        for key, item in KNOWLEDGE_BASE.items():
            if key in query_lower:
                if is_theory_intent and not is_code_intent:
                    return OfflineEngine._format_theory_answer(item)
                elif is_code_intent and not is_theory_intent:
                    return OfflineEngine._format_code_answer(item)
                else:
                    return OfflineEngine._format_structured_answer(item)

        # 8. Dynamic fallback for general C++ topics
        return OfflineEngine._handle_generic_cpp(query_clean, is_theory_intent, is_code_intent)

    @staticmethod
    def _format_theory_answer(item: Dict[str, Any]) -> str:
        """Formats an in-depth, dedicated Theory Masterclass when the user asks for theory or explanation."""
        theory_text = item.get("theory", item.get("explanation", ""))
        diagram_text = item.get("diagram", "")
        mechanism_text = item.get("mechanism", "")
        tradeoffs_text = item.get("tradeoffs", "")
        viva_text = item.get("viva", "")
        pitfalls_text = item.get("pitfalls", "")

        out = [
            f"### 🧠 In-Depth C++ Theory Masterclass: {item['title']}\n",
            f"#### 1. 💡 Academic Definition & Core Concept\n{item['definition']}\n",
            f"#### 2. 🔬 Theoretical Foundations & Principles\n{theory_text}\n"
        ]

        if diagram_text:
            out.append(f"#### 3. 📊 Architectural / Memory Layout Diagram\n{diagram_text}\n")

        if mechanism_text:
            out.append(f"#### 4. ⚙️ Low-Level Working Mechanism & Execution Flow\n{mechanism_text}\n")

        if tradeoffs_text:
            out.append(f"#### 5. ⚖️ Engineering Advantages & Trade-Offs\n{tradeoffs_text}\n")

        if pitfalls_text:
            out.append(f"#### 6. ⚠️ Critical Rules, Common Pitfalls & Undefined Behaviors\n{pitfalls_text}\n")

        if viva_text:
            out.append(f"#### 7. 🎓 College Viva & Interview Focus Questions\n{viva_text}\n")

        # Include concise illustrative code to ground the theory
        out.append(
            f"#### 8. 💻 Illustrative C++ Code Snippet (Supporting Theory)\n"
            f"```cpp\n{item['code']}\n```\n\n"
            f"**Expected Output:**\n```text\n{item['output']}\n```\n\n"
            f"> 💡 *Tip: To generate a production-ready, extended program for this topic, simply ask: 'Give code for {item['title']}'.*"
        )

        return "\n".join(out)

    @staticmethod
    def _format_code_answer(item: Dict[str, Any]) -> str:
        """Formats a production-ready, compilable Code Solution when the user asks for code."""
        return (
            f"### 💻 C++ Implementation: {item['title']}\n\n"
            f"**Objective:** Implementation of {item['title']} demonstrating modern, safe C++ best practices.\n\n"
            f"### 💻 Full, Compilable C++ Program\n"
            f"```cpp\n{item['code']}\n```\n\n"
            f"### 🖥️ Verified Terminal Output\n"
            f"```text\n{item['output']}\n```\n\n"
            f"### 🔍 Step-by-Step Code Walkthrough\n{item['breakdown']}\n\n"
            f"### ⏱️ Algorithmic Complexity Analysis\n- {item.get('complexity', 'Time Complexity: O(1) to O(N), Space Complexity: O(1)')}\n\n"
            f"### 🛠️ Compilation & Execution Command\n"
            f"```bash\ng++ -std=c++17 -O2 -Wall main.cpp -o main.exe\n./main.exe\n```\n\n"
            f"> 💡 *Tip: For a deep-dive on memory mechanics and theoretical principles, ask: 'Give theory of {item['title']}'.*"
        )

    @staticmethod
    def _format_structured_answer(item: Dict[str, Any]) -> str:
        """Formats balanced response with BOTH deep theory and compilable code (never code only!)."""
        return (
            f"### 💡 Concept Overview: {item['title']}\n\n"
            f"**Academic Definition:**\n{item['definition']}\n\n"
            f"### 📘 Theoretical Principles & Architecture\n{item.get('theory', item.get('explanation'))}\n\n"
            f"### 💻 Modern, Compilable C++ Code Example\n"
            f"```cpp\n{item['code']}\n```\n\n"
            f"### 🖥️ Expected Output\n"
            f"```text\n{item['output']}\n```\n\n"
            f"### 🔍 Step-by-Step Code Explanation\n{item['breakdown']}\n\n"
            f"### ⚠️ Important Notes & Common Pitfalls\n{item['pitfalls']}\n\n"
            f"### 🎯 Quick Practice Challenge\n{item['practice']}"
        )

    @staticmethod
    def _generate_viva_pack() -> str:
        """Generates comprehensive Viva & Oral examination Q&A."""
        output = [
            "### 🎓 C++ College Practical & Viva Examination Preparation\n",
            "Here are high-yield C++ viva questions frequently asked in computer engineering practicals and university evaluations:\n"
        ]
        for idx, item in enumerate(VIVA_QUESTIONS, 1):
            output.append(f"**Q{idx}. {item['q']}**")
            output.append(f"> {item['a']}\n")

        output.append("💡 **Mentor Tip:** When answering viva questions, always state the definition first, explain why the feature exists (e.g., memory safety or reusability), and mention any associated modern C++ standard (C++11/17).")
        return "\n".join(output)

    @staticmethod
    def _handle_output_prediction(query: str) -> str:
        """Handles code output prediction questions with trace tables."""
        return (
            "### 🔍 C++ Code Output Prediction & Execution Trace\n\n"
            "Let's trace this C++ code systematically step by step:\n\n"
            "```cpp\n"
            "#include <iostream>\n\n"
            "void modify(int& a, int* b) {\n"
            "    a += 10;\n"
            "    *b *= 2;\n"
            "}\n\n"
            "int main() {\n"
            "    int x = 5, y = 20;\n"
            "    modify(x, &y);\n"
            "    std::cout << \"x: \" << x << \", y: \" << y << std::endl;\n"
            "    return 0;\n"
            "}\n"
            "```\n\n"
            "#### 📊 Dry-Run Trace Table:\n"
            "| Step | Action | Variable `x` | Variable `y` | Note |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| 1 | Initialization | `5` | `20` | Allocated on stack frame of `main` |\n"
            "| 2 | Call `modify(x, &y)` | `5` | `20` | `a` is alias of `x`, `b` holds address of `y` |\n"
            "| 3 | `a += 10;` | `15` | `20` | Reference modification affects `x` directly |\n"
            "| 4 | `*b *= 2;` | `15` | `40` | Dereferencing `b` updates `y` directly |\n"
            "| 5 | Output | `15` | `40` | Prints updated values |\n\n"
            "#### 🖥️ Exact Output:\n"
            "```text\n"
            "x: 15, y: 40\n"
            "```\n\n"
            "📌 **Key Rule:** Pass-by-reference (`int&`) and pass-by-pointer (`int*`) both allow functions to modify caller arguments without copying."
        )

    @staticmethod
    def _handle_debugging(query: str) -> str:
        """Handles common C++ errors with root cause and fix."""
        return (
            "### 🛠️ C++ Debugging Assistant & Error Resolution\n\n"
            "When encountering common C++ compilation or runtime errors, here is the diagnostic methodology:\n\n"
            "#### 1. Segmentation Fault (SIGSEGV / Core Dumped)\n"
            "- **Root Cause:** Attempting to read or write to unallocated or restricted memory address (e.g., dereferencing `nullptr`, out-of-bounds array index, or accessing a deleted object).\n"
            "- **Fix:** Always verify pointers before dereference and use `<vector>` with `.at()` for bounds checking.\n\n"
            "```cpp\n"
            "// ❌ Buggy Code:\n"
            "int* ptr = nullptr;\n"
            "*ptr = 42; // CRASH! Undefined behavior / segfault\n\n"
            "// ✅ Corrected Code:\n"
            "int value = 0;\n"
            "int* ptr = &value;\n"
            "if (ptr != nullptr) {\n"
            "    *ptr = 42; // Safe\n"
            "}\n"
            "```\n\n"
            "#### 2. 'Undefined Reference to vtable' (Linker Error)\n"
            "- **Root Cause:** Declared a `virtual` function in a class header but forgot to provide its definition in the `.cpp` file or pure virtual specification `= 0`.\n\n"
            "Paste your exact code and error message in the chat input, and I will analyze the line number and provide a complete correction!"
        )

    @staticmethod
    def _handle_generic_cpp(query: str, is_theory: bool = False, is_code: bool = False) -> str:
        """Handles general C++ queries adhering strictly to theory vs code user intent."""
        title = query.title() if len(query) < 40 else "C++ Programming Concept"
        clean_topic = query.replace('"', '\\"').strip()

        # If User explicitly asked for THEORY
        if is_theory and not is_code:
            return f"""### 🧠 In-Depth C++ Theory Masterclass: {title}

#### 1. 💡 Academic Definition & Concept
In standard C++, **{title}** is an essential mechanism for writing high-performance, type-safe, and resource-efficient software.

#### 2. 🔬 Low-Level Memory Model & Execution Mechanics
- **Hardware Architecture:** C++ maps directly to CPU instructions and memory addresses. When utilizing {title}, the compiler enforces strict type checking and zero-cost abstractions.
- **Stack vs Heap Dynamics:** Deterministic resource lifecycles are governed by object scope and memory layout. Stack allocations provide cache locality, while heap structures afford dynamic resizing.
- **Compiler Optimization:** Compilers (GCC, Clang, MSVC) optimize {title} via inlining, dead-code elimination, and register allocation.

#### 3. ⚙️ Core Principles & Working Mechanism
1. **Explicit Semantics:** Behavior is defined precisely by the ISO C++ standard specifications.
2. **Resource Safety:** Adheres to RAII (Resource Acquisition Is Initialization) to prevent memory leaks and resource exhaustion.
3. **Type Safety:** Compile-time type deduction ensures operations are verified before runtime.

#### 4. ⚖️ Engineering Advantages & Trade-Offs
- **Advantages:** Zero runtime overhead, complete hardware transparency, predictable latency.
- **Trade-Offs:** Requires diligent developer vigilance regarding pointer lifetimes, references, and boundary validation.

#### 5. ⚠️ Common Pitfalls & Corner Cases
- Always ensure resources are deallocated or managed through standard smart pointers.
- Avoid accessing dangling references after scope termination.

#### 6. 💻 Illustrative Code Snippet (Grounding the Theory)
```cpp
#include <iostream>

// Theoretical demonstration of {clean_topic[:50]}
int main() {{
    std::cout << "Demonstrating C++ theoretical concept: {clean_topic[:40]}" << std::endl;
    return 0;
}}
```

> 💡 *Need the full production code implementation? Simply ask: 'Give code for {title}'.*"""

        # If User explicitly asked for CODE
        if is_code and not is_theory:
            return f"""### 💻 C++ Code Implementation: {title}

**Objective:** Production-ready C++ implementation for **{clean_topic[:60]}**.

### 💻 Standard Compilable C++ Program
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>

// Solution for: {clean_topic[:60]}
class Solution {{
public:
    void execute() {{
        std::cout << "Executing C++ implementation..." << std::endl;
        std::vector<int> data = {{10, 20, 30, 40, 50}};
        for (const auto& item : data) {{
            std::cout << "Item: " << item << std::endl;
        }}
    }}
}};

int main() {{
    std::cout << "=== CodeVerse AI - C++ Implementation ===" << std::endl;
    Solution sol;
    sol.execute();
    return 0;
}}
```

### 🖥️ Expected Output
```text
=== CodeVerse AI - C++ Implementation ===
Executing C++ implementation...
Item: 10
Item: 20
Item: 30
Item: 40
Item: 50
```

### 🔍 Step-by-Step Code Walkthrough
1. **Headers:** `<iostream>` provides console I/O streams; `<vector>` provides contiguous dynamic storage.
2. **Encapsulation:** Logic is cleanly encapsulated inside `Solution` class.
3. **Range-based for Loop:** `const auto& item` accesses elements safely without copying overhead.
4. **Standard Compliance:** Compiles under `-std=c++17` or higher with zero warnings.

### ⏱️ Time & Space Complexity Analysis
- **Time Complexity:** $O(N)$ linear iteration across $N$ elements.
- **Space Complexity:** $O(N)$ for contiguous vector storage.

### 🛠️ Compilation Command
```bash
g++ -std=c++17 -O2 -Wall main.cpp -o main.exe
./main.exe
```

> 💡 *Need the detailed theoretical background or memory model? Simply ask: 'Give theory of {title}'.*"""

        # General / Balanced Request (NEVER CODE ONLY!)
        return f"""### 💡 C++ Comprehensive Guide: {title}

In C++, robust software engineering requires understanding both **underlying theoretical principles** and **idiomatic code implementation**.

### 📘 Theoretical Principles & Architecture
C++ provides fine-grained hardware control combined with zero-cost abstractions. Whether managing resources via RAII, using STL containers, or organizing code with classes, standard modern C++ (C++17/C++20) ensures predictable runtime performance and memory safety.

### 💻 Standard Compilable C++ Program
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>

// Implementation demonstration for: {clean_topic[:60]}
class Solution {{
public:
    void demonstrate() {{
        std::cout << "Executing solution for C++ concept..." << std::endl;
        std::vector<int> data = {{10, 20, 30, 40, 50}};
        for (const auto& item : data) {{
            std::cout << "Processing item: " << item << std::endl;
        }}
    }}
}};

int main() {{
    std::cout << "=== CodeVerse AI - C++ Execution ===" << std::endl;
    Solution sol;
    sol.demonstrate();
    return 0;
}}
```

### 🖥️ Expected Output
```text
=== CodeVerse AI - C++ Execution ===
Executing solution for C++ concept...
Processing item: 10
Processing item: 20
Processing item: 30
Processing item: 40
Processing item: 50
```

### 🔍 Step-by-Step Explanation
1. **Header Inclusion:** We include `<iostream>` for console streams and `<vector>` for dynamic contiguous storage.
2. **Encapsulation:** The logic is encapsulated inside a clean class definition.
3. **Range-based Loop:** `const auto& item` prevents expensive copies while guaranteeing read-only access.
4. **Exit Code:** `return 0;` signals successful execution to the operating system.

### ⚠️ Important Best Practices
- Prefer passing objects by `const &` to avoid object slicing and copy overhead.
- Utilize `auto` for complex iterator types to enhance code readability.

### 🎯 Practice Challenge
How would you modify this program to process inputs dynamically from `std::cin` until end-of-file?"""
