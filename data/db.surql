-- create db
define namespace wtt;
define database wtt;

define login admin on namespace password 'password';

use ns wtt db wtt;

-- create tables
define table interviewers schemafull;
define table interviewees schemafull;
define table tests schemafull;

-- define `interviewers` fields
let $interviewers_tags = ['admin'];

define field id 
    on table interviewers 
    type string
    assert $value != none 
        and string::startsWith($value, '@');
define field name 
    on table interviewers 
    type string
    assert $value != none 
        and string::len($value) != 0;
define field description 
    on table interviewers 
    type string;
define field tags
    on table interviewers
    type array
    value $value or ['admin']
    assert $value inside $interviewers_tags;
define field tags.*
    on table interviewers
    type string;
define field tests
    on table interviewers
    type array;
define field tests.*
    on table interviewers
    type record(tests);

-- define `interviewees` fields
define field id 
    on table interviewees 
    type string
    assert $value != none 
        and string::startsWith($value, '@');
define field name 
    on table interviewees 
    type string
    assert $value != none 
        and string::len($value) != 0;
define field description 
    on table interviewees 
    type string;
define field tags
    on table interviewees
    type array
    assert array::len($value) != 0;
define field tags.*
    on table interviewees
    type string;

-- define `tests` fields
define field id
    on table tests
    type string
    assert is::uuid($value);
define field name 
    on table tests 
    type string
    assert $value != none 
        and string::len($value) != 0;
define field description 
    on table tests 
    type string;
define field tags
    on table tests
    type array
    assert array::len($value) != 0;
define field tags.*
    on table tests
    type string;
define field authors
    on table tests
    type array
    assert $value != none
        and array::len($value) != 0;
define field authors.*
    on table tests
    type record(interviewers);
define field constraints
    on table tests
    type object;
define field questions
    on table tests
    type array;
define field questions.*
    on table tests
    type object;