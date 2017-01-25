import sys
import json
import jsonschema
import pystache
import os

def isDict(obj):
    return isinstance(obj, dict)

def isList(obj):
    return isinstance(obj, list)

def isString(obj):
    return isinstance(obj, str)

def isNumber(obj):
    return isinstance(obj, (int, float))

def isBool(obj):
    return isinstance(obj, bool)

_ospath = None
def loadFile(aPath, aName, aSuffix):
    global _ospath
    if not _ospath:
        encoding = sys.getfilesystemencoding()
        _ospath = os.path.dirname(unicode(__file__, encoding))

    lfileName = os.path.join(_ospath, aPath, "%s.%s" % (aName, aSuffix))
    
    #print lfileName
    with open(lfileName) as f:
        retval = f.read()
    #print retval
    return retval    
    
def loadJsonSchema(aName):
    lschemaStr = loadFile("schema", aName, "schema.json")
    lschema = json.loads(lschemaStr)
    #print lschema
    return lschema

def validate(aObj, aSchemaName):
    lschema = loadJsonSchema(aSchemaName)
    jsonschema.validate(aObj, lschema)

def matches(aObj, aSchemaName):
    lschema = loadJsonSchema(aSchemaName)
    try:
        jsonschema.validate(aObj, lschema)
        return True
    except:
        return False

class FailException(Exception):
    def __init__(self, result, message):
        Exception.__init__(self, message)
        self.result = result

def AddIndent(aInput, aIndent):
    llines = aInput.split("\n")
    loutLines = []
    aIndentStr = "  " * aIndent
    for lline in llines:
        loutLines.append("%s%s" % (aIndentStr, lline))
    return "\n".join(loutLines)

def RenderPystache(aLanguage, aIStatement, aTemplateName):    
    ltemplateStr = loadFile("templates/%s" % aLanguage, aTemplateName, "mustache")
    
#     print ltemplateStr
#     print aIStatement
     
    return pystache.render(ltemplateStr, aIStatement)
    
def RenderLiteral(aLanguage, aIStatement, aIndent):
    retval = json.dumps(aIStatement["lit"], indent=2)
    
    return retval
    
def RenderDeclFunc(aLanguage, aIStatement, aIndent):
    lstatement = {
        "declfunc": aIStatement["declfunc"],
        "hasbody": not not aIStatement.get("body")
    }

    if aIStatement.get("args"):
        lstatement["firstarg"] = aIStatement.get("args")[0]
        lstatement["moreargs"] = aIStatement.get("args")[1:]

    
    if "body" in aIStatement:
        lstatement["body"] = RenderIStatementBlock(aLanguage, aIStatement["body"], aIndent)
        
    retval = RenderPystache(aLanguage, lstatement, "declfunc")
    
    return retval

def RenderCallFunc(aLanguage, aIStatement, aIndent):
    lstatement = {
        "callfunc": aIStatement["callfunc"]
    }

    if aIStatement.get("args"):
        largs = [RenderIStatement(aLanguage, larg, aIndent) for larg in aIStatement.get("args")]
        lstatement["args"] = largs
        lstatement["firstarg"] = largs[0]
        lstatement["moreargs"] = largs[1:]
        
    retval = RenderPystache(aLanguage, lstatement, "callfunc")
    
    return retval

def RenderAssign(aLanguage, aIStatement, aIndent):
    lstatement = {
        "assign": aIStatement["assign"],
        "value": RenderIStatement(aLanguage, aIStatement["value"], aIndent)
    }

    retval = RenderPystache(aLanguage, lstatement, "assign")
    
    return retval

def RenderDeclVar(aLanguage, aIStatement, aIndent):
    lstatement = {
        "declvar": aIStatement["declvar"]
    }
    
    if "default" in aIStatement:
        lstatement["default"] = RenderIStatement(aLanguage, aIStatement["default"], aIndent)

    retval = RenderPystache(aLanguage, lstatement, "declvar")
    
    return retval

def RenderComment(aLanguage, aIStatement, aIndent):
    retval = RenderPystache(aLanguage, aIStatement, "comment")
    
    return retval

def RenderBinOp(aLanguage, aIStatement, aIndent):
    lstatement = {
        "op": aIStatement[0],
        "left": RenderIStatement(aLanguage, aIStatement[1], aIndent),
        "right": RenderIStatement(aLanguage, aIStatement[2], aIndent),
    }
    
    retval = RenderPystache(aLanguage, lstatement, "binop")
    
    return retval

def RenderEqual(aLanguage, aIStatement, aIndent):
    lstatement = {
        "left": RenderIStatement(aLanguage, aIStatement[1], aIndent),
        "right": RenderIStatement(aLanguage, aIStatement[2], aIndent),
    }
    
    retval = RenderPystache(aLanguage, lstatement, "equal")
    
    return retval

def RenderForEach(aLanguage, aIStatement, aIndent):
    lstatement = {
        "for": aIStatement["for"],
        "in": RenderIStatement(aLanguage, aIStatement["in"], aIndent),
        "do": RenderIStatementBlock(aLanguage, aIStatement["do"], aIndent),
    }
    
    retval = RenderPystache(aLanguage, lstatement, "foreach")
    
    return retval

def RenderVar(aLanguage, aIStatement, aIndent):
    retval = RenderPystache(aLanguage, aIStatement, "var")
    
    return retval

def RenderReturn(aLanguage, aIStatement, aIndent):
    lstatement = {
        "value": RenderIStatement(aLanguage, aIStatement["return"], aIndent)
    }
    
    retval = RenderPystache(aLanguage, lstatement, "return")
    
    return retval

def RenderNot(aLanguage, aIStatement, aIndent):
    lstatement = {
        "value": RenderIStatement(aLanguage, aIStatement[1], aIndent)
    }
    
    retval = RenderPystache(aLanguage, lstatement, "not")
    
    return retval

def RenderIf(aLanguage, aIStatement, aIndent):
    lstatement = {
        "if": RenderIStatement(aLanguage, aIStatement["if"], aIndent),
        "then": RenderIStatementBlock(aLanguage, aIStatement["then"], aIndent)
    }
    
    if aIStatement.get("elsif"):
        lstatement["elsif"] = [{
            "if": RenderIStatement(aLanguage, lsection["if"], aIndent),
            "then": RenderIStatementBlock(aLanguage, lsection["then"], aIndent)
          }
          for lsection in aIStatement.get("elsif")
        ]
        
    if aIStatement.get("else"):
        lstatement["else"] = RenderIStatementBlock(aLanguage, aIStatement["else"], aIndent)
    
    retval = RenderPystache(aLanguage, lstatement, "if")
    
    return retval

def RenderWhile(aLanguage, aIStatement, aIndent):
    lstatement = {
        "while": RenderIStatement(aLanguage, aIStatement["while"], aIndent),
        "do": RenderIStatementBlock(aLanguage, aIStatement["do"], aIndent)
    }
    
    retval = RenderPystache(aLanguage, lstatement, "while")
    
    return retval

def RenderIStatementBlock(aLanguage, aIStatementBlock, aIndent):
    lrenderedStatements = [AddIndent(RenderIStatement(aLanguage, lIStatement, aIndent+1), aIndent+1) for lIStatement in aIStatementBlock]
    lblock = {
        "body": lrenderedStatements,
        "hasbody": not not lrenderedStatements
    }
    retval = RenderPystache(aLanguage, lblock, "block")
    retval = AddIndent(retval, aIndent)
    return retval

_dispatch = [
 ["literal", RenderLiteral],
 ["declfunc", RenderDeclFunc],
 ["assign", RenderAssign],
 ["comment", RenderComment],
 ["declvar", RenderDeclVar],
 ["binop", RenderBinOp],
 ["foreach", RenderForEach],
 ["var", RenderVar],
 ["if", RenderIf],
 ["equal", RenderEqual],
 ["return", RenderReturn],
 ["not", RenderNot],
 ["while", RenderWhile],
 ["callfunc", RenderCallFunc]
]
     
def RenderIStatement(aLanguage, aIStatement, aIndent):
    lmatch = False
    for lschemaName, lrenderFunc in _dispatch:
        lmatch = matches(aIStatement, lschemaName)
        if lmatch:
            retval = lrenderFunc(aLanguage, aIStatement, aIndent)
            break
    
    if not lmatch:
        if not isDict(aIStatement) and not isList(aIStatement):
            retval = RenderLiteral(aLanguage, {"lit": aIStatement}, aIndent)
        else:
            raise FailException(200, "Can't render this IStatement: %s" % json.dumps(aIStatement, 2))

    return retval
    
def interesting(aLanguage, aIProg):
    retval = ""
    
    try:
        validate(aIProg, "iprog")
    except Exception as ex:
        raise FailException(100, "iprog not valid\n%s\n" % str(ex))

    if not "main" in aIProg:
        print "Warning: No main found in iprog"

#     with open('test.txt', 'w') as f:
    if "pre" in aIProg:
        for litem in aIProg["pre"]:
            litemRendered = RenderIStatement(aLanguage, litem, 0)
            if litemRendered:
                retval = "%s\n%s\n" % (retval, litemRendered)
                
    if "main" in aIProg:
        litemRendered = RenderIStatement(aLanguage, aIProg["main"], 0)
        if litemRendered:
            retval = "%s\n%s\n" % (retval, litemRendered)
        
    if retval:
        retval += "\n"
    
    return retval

def main():
    largs = sys.argv;

    llanguage = None    
    lfilename = None
    
    if len(largs) < 2:
        raise FailException(10, "Usage: interesting <language>[ <infile>[ <outfile>]]\n  language: javascript or python")
    else:
        llanguage = largs[1]
        if len(largs) > 2:
            lfilename = largs[2]
            
    if not llanguage in ["javascript", "python"]:
        raise FailException(20, "Language must be javascript or python")

    if lfilename:
        inf = open(lfilename)
    else:
        inf = sys.stdin            

    liprog = None
    try:
        liprog = json.load(inf)
    except Exception as ex:
        raise FailException(30, "Failed to read iprog\n%s\n" % str(ex))
    finally:
        if lfilename:
            inf.close()

    retval = interesting(llanguage, liprog)
    
    return retval


if __name__ == "__main__":
    try:
        exit(main())
    except FailException as fex:
        print("Fail %s: %s" % (fex.result, str(fex)))
