quark *;
void test() {
    x = ${this is directly emitted};
    y = ${this is directly emitted with $substitution};
    z = ${this is directly emitted{} with {$substitution}};
    a = ${ this is a test{ of $asdf $fdsa  {} } };
    b = $java{this is a test of java native stuff};
    c = $java{this is java}
        $py{this is python};
    d = $java{this is java}
        $py{this is python}
	${this is default};
}
