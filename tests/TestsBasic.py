import unittest
from interesting import interesting
from Util import deepEqual, copyjson

class TestsBasic(unittest.TestCase):
    def deepCheck(self, lexpected, lresult):
        lpassed = deepEqual(lexpected, lresult)
        if not lpassed:
            print "expected(%s): %s" % (len(lexpected), lexpected)
            print "result(%s): %s" % (len(lresult), lresult)
            self.assertTrue(lpassed, "result doesn't match expected")

    def stringCheck(self, lexpected, lresult):
        lpassed = lexpected.strip() == lresult.strip()
        if not lpassed:
            print "expected(%s): %s" % (len(lexpected), lexpected)
            print "result(%s): %s" % (len(lresult), lresult)
            self.assertTrue(lpassed, "result doesn't match expected")
            
    def test1(self):
        lsrcprog = {
        }
        
        lresult = interesting("python", copyjson(lsrcprog))

        self.deepCheck("", lresult)
        
    def test2(self):
        lsrcprog = {
            "main": {
                "lit": "x"
            }
        }
        
        lresult = interesting("python", copyjson(lsrcprog))

        lexpected = """
"x"
"""
        self.stringCheck(lexpected, lresult)
        
    def test3(self):
        lsrcprog = {
            "main": {
                "declfunc": "main",
                "args": ["argv"],
                "body": [
                    {
                        "assign": "retval",
                        "value": {
                            "lit": {
                                "x": 2
                            }
                        }
                    }
                ]
            }
        }
        
        lresult = interesting("javascript", copyjson(lsrcprog))

        lexpected = """
function main (argv)
{
  retval = {
    "x": 2
  };
};
"""
        self.stringCheck(lexpected, lresult)
        
    def testComment(self):
        lsrcprog = {
            "main": {
                "comment": [
                    "first line",
                    "second line"
                ]
            }
        }
        
        lresult = interesting("python", copyjson(lsrcprog))

        lexpected = """
# first line
# second line
"""
        self.stringCheck(lexpected, lresult)
        
    def testDeclVar(self):
        lsrcprog = {
            "pre": [
                {
                    "declvar": "x",
                    "default": 1
                }
            ]
        }
        
        lresult = interesting("javascript", copyjson(lsrcprog))

        lexpected = """
var x = 1;
"""
        self.stringCheck(lexpected, lresult)
        
    def testBinOp(self):
        lsrcprog = {
            "main": {
                "assign": "x",
                "value": ["+", 5, 3]
            }
        }
        
        lresult = interesting("python", copyjson(lsrcprog))

        lexpected = """
x = (5 + 3)
"""
        self.stringCheck(lexpected, lresult)
        
        
    def testForEach(self):
        lsrcprog = {
            "pre": [
                {
                    "assign": "glist",
                    "value": {
                        "lit": [1, 2, 3, 4, 5]
                    }
                }
            ],
            "main": {
                "for": "x",
                "in": {
                    "var": "glist"
                },
                "do": [
                    
                ]
            }
        }
        
        lresult = interesting("python", copyjson(lsrcprog))

        lexpected = """
glist = [
  1, 
  2, 
  3, 
  4, 
  5
]

for x in glist:
  pass
"""
        self.stringCheck(lexpected, lresult)
        
    def testIf(self):
        lsrcprog = {
            "main": {
                "if": ["==", {"var": "x"}, 3],
                "then": [
                    {
                        "assign": "y",
                        "value": 1
                    }
                ],
                "elsif": [
                    {
                        "if": ["==", {"var": "x"}, 4],
                        "then": [
                            {
                                "assign": "y",
                                "value": 2
                            }
                        ]
                    }
                ],
                "else": [
                    {
                        "assign": "y",
                        "value": 3
                    },
                    {
                        "assign": "y",
                        "value": 4
                    }
                ]
            }
        }
        
        lresult = interesting("python", copyjson(lsrcprog))

        lexpected = """
if (x == 3):
  y = 1
elsif (x == 4):
  y = 2
else:
  y = 3
  y = 4
"""
        self.stringCheck(lexpected, lresult)
        
    def testReturn(self):
        lsrcprog = {
            "main": { 
              "return": 3
            }
        }
        
        lresult = interesting("python", copyjson(lsrcprog))

        lexpected = """
return 3
"""
        self.stringCheck(lexpected, lresult)
        
    def testNot(self):
        lsrcprog = {
            "main": [ "not", {"var": "x"} ] 
        }
        
        lresult = interesting("javascript", copyjson(lsrcprog))

        lexpected = """
(! x)
"""
        self.stringCheck(lexpected, lresult)
        
    def testWhile(self):
        lsrcprog = {
            "main": {
                "while": ["not", {"var": "found"}],
                "do": [
                    {
                        "assign": "x",
                        "value": ["+", {"var": "x"}, 1]
                    }
                ] 
            }
        }
        
        lresult = interesting("javascript", copyjson(lsrcprog))

        lexpected = """
while ((! found))
{
  x = (x + 1);
};
"""
        self.stringCheck(lexpected, lresult)
        
    def testCallFunc(self):
        lsrcprog = {
            "main": {
                "callfunc": "f",
                "args": [{"var": "x"}, "a", ["not", {"var": "z"}]]
            }
        }
        
        lresult = interesting("javascript", copyjson(lsrcprog))

        lexpected = """
f (x, "a", (! z))
"""
        self.stringCheck(lexpected, lresult)
        