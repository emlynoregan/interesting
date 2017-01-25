import json

def deepEqual(aMAS1, aMAS2, maxdepth=100):
    retval = False

    if maxdepth:
        retval = type(aMAS1) == type(aMAS2)
        if retval:
            if isinstance(aMAS1, dict):
                retval = len(aMAS1.keys()) == len(aMAS2.keys())
                if retval:
                    for lkey in aMAS1.keys():
                        retval = lkey in aMAS2 and deepEqual(aMAS1[lkey], aMAS2[lkey], maxdepth-1)
                        if not retval:
                            break
            elif isinstance(aMAS1, (list, tuple, set)):
                retval = len(aMAS1) == len(aMAS2)
                if retval:
                    for lindex, litem in enumerate(aMAS1):
                        retval = deepEqual(litem, aMAS2[lindex], maxdepth-1)
                        if not retval:
                            break
            else:
                retval = aMAS1 == aMAS2
        
    return retval

def copyjson(aObj):
    return json.loads(json.dumps(aObj))
    