import random
import math
import time
import millvar  # global simulation variables and datatypes are kept here
from coillists import *

nextCoil_DefectList = {}
debugPrint = False  # print debug info
printPipes = False  # print pipes created
richOptimize = True # use new optimize function
autoCoils= True    # Generate random coils
autoDefects = False # Create random steel mill induced defects
autoMillStop = False # Create random mill stops in generated data
runPrint = 1
# set to 1 will generate millstops as part of coil creation
# set to 0 will randomly generate mill stops each time a coil is run
millvar.no_live_stops = 1

# parameter = 0 means no defects 1 is use defects
generate_defects = 0

if millvar.no_live_stops == 1:
    generate_defects = 0

newpipes = []
millvar.cutlist = []
millvar.nextbad = []
coilpipes = []

# a list of every pipe produced in the simulation
# the format of the pipeid indicates mill stop frequency,
# run number for the frequency, the coil number and the pipe number
#  XXYY ZZZZ AA
#                  XX = mill stop frequency per 10000 ft
#                  YY = the run/interation at the specified frequency
#                ZZZZ = the coil number from the run
#                  AA = the pipe number from the coil
masterpipes = []



# Generate test coil data for simulation run defects here are furnace tears
def create_simulation_coil_list(num_coils):
    coillist = []
    if autoCoils:
        for i in range(0, num_coils ):
            coil_length = random.randint(millvar.coil_Minimum_Length, millvar.coil_Maximum_Length)
            if autoDefects:
                def_1 = random.randint(0, coil_length) * random.randint(0, 1) * generate_defects
                def_2 = random.randint(0, coil_length) * random.randint(0, 1) * generate_defects
                def_3 = random.randint(0, coil_length) * random.randint(0, 1) * generate_defects
                # def_4 is used to create coil based mill stops instead of random stops
                # using the no_live-stops flag
            else:
                def_1 = 0
                def_2 = 0
                def_3 = 0
            if autoMillStop:
                addmillstop = random.randint(0, 10)
                if addmillstop <= 2:
                    def_4 = random.randint(20, coil_length - 10)
                else:
                    def_4 = 0
            else:
                def_4 = 0
            coil = [coil_length, def_1, def_2, def_3, def_4]
            coillist.append(coil)
    else:
        coillist =  coillist1()


    return coillist







# return amount of scrap based on defect length and pipelength
def calc_scrap(defect_len, pipe_len):
    if defect_len == millvar.tear_BadLength:
        scrap = defect_len
    if defect_len == millvar.crossweld_BadLength:
        scrap = defect_len
    else:
        scrap = defect_len

    return scrap


######################################################################################
#  Get defects from previous Coil
#
#

def get_Prev_Coil_Defects():
    defectlist = []
    for key in nextCoil_DefectList:

        defect = nextCoil_DefectList[key]
        dLoc = int(defect.location)
        dLen = defect.length
        dType = defect.defect_type
        dLoc = dLoc + millvar.headChop
        # if defect location is less than zero then the defect position is now
        # zero and the length of the defect is shortend by the negative location amount
        #
        if dLoc < 0:
            dLen += dLoc
            dLoc = 0
        newdefect = millvar.Defect(dLoc, dLen, dType)

        defectid = int(dLoc)
        if runPrint == 1:
            print("added from previous coil mill stop", newdefect)
        defectlist.append(newdefect)
        # print defectlist
        # for defect in defectlist:
        # print defect

    # print "new defectlist",defectlist

    return defectlist


################################################################################
# Load a coil to run
# inputs: coil , headChop(amount borrowed by previous coil)
# Returns defect list
def load_Coil(coil, headChop):
    coil_DefectList = {}
    millvar.crush_test = True


    # running_Coil_Length = coil[0]*1.0
    # crossweld_Location = coil[0]*1.0
    if debugPrint:
        print('\nLoad Coil- enter load_Coil headchop = ',headChop)
        print('Coil in = ',coil)
        print('defects:', coil[1], millvar.tear_BadLength, ' ft',
              coil[2], millvar.tear_BadLength, ' ft',
              coil[3], millvar.tear_BadLength, ' ft   static mill stop at',
              coil[4], ' ft\n')
    # Always account for crossweld on each coil
    # headChop -=  millvar.crossweld_BadLength

    # create defect at crossweld
    # newdefect = millvar.Defect(coil[0] + headChop, millvar.crossweld_BadLength, 1)
    # Add crossweld defect at end of coil
    newdefect = millvar.Defect(coil[0] + headChop, millvar.crossweld_BadLength, 1)
    # newdefect = millvar.Defect(coil[0], millvar.crossweld_BadLength, 1)
    # add defects that came from steel mill
    defectid = int(newdefect.location)
    coil_DefectList[defectid] = newdefect

    if coil[1] > 0:
        newdefect = millvar.Defect(coil[1] + headChop, millvar.tear_BadLength, 2)
    else:
        newdefect = millvar.Defect(coil[1], millvar.tear_BadLength, 2)
    defectid = int(newdefect.location)
    coil_DefectList[defectid] = newdefect

    if coil[2] > 0:
        newdefect = millvar.Defect(coil[2] + headChop, millvar.tear_BadLength, 2)
    else:
        newdefect = millvar.Defect(coil[2], millvar.tear_BadLength, 2)
    defectid = int(newdefect.location)
    coil_DefectList[defectid] = newdefect

    if coil[3] > 0:
        newdefect = millvar.Defect(coil[3] + headChop, millvar.tear_BadLength, 2)
    else:
        newdefect = millvar.Defect(coil[3], millvar.tear_BadLength, 2)
    defectid = int(newdefect.location)
    coil_DefectList[defectid] = newdefect
    if debugPrint:
        print('exit load_coil  defects: ', coil_DefectList)

    return coil_DefectList


################################################################################
# clean up the defect list by removing entries that are negative locations
# since they no longer matter
def clean_Defects(coil_DefectList):
    newdefects = []
    for key in coil_DefectList:
        defect = coil_DefectList[key]
        # dLoc = math.ceil((defect.location))
        dLoc = round(defect.location, 1)
        dLen = defect.length
        dType = defect.defect_type
        if dLoc >= 0:
            newdefect = millvar.Defect(dLoc, dLen, dType)
            newdefects.append(newdefect)

            # Rewrite list after cleanup
    coil_DefectList.clear()
    for defect in newdefects:
        defectid = int(defect.location)
        if defectid > 0:
            coil_DefectList[defectid] = defect
    return coil_DefectList


# return the coil length which is the maximum defect location in a coil
def get_coil_length(coil_list):
    coil_len = 0.0

    for key in coil_list:
        defect = coil_list[key]
        length = defect.location
        if length > coil_len:
            coil_len = length

    return coil_len


# Get distance to closest defect
def get_ClosestDefect(coil_DefectList):
    # print('Defect list length = ', len(coil_DefectList))
    # print('get closest defect list = ',coil_DefectList)
    closestkey = 10000
    for key in coil_DefectList:
        if key < closestkey:
            closestkey = key

    return closestkey


def get_Next_Closest_Defect(closest, coil_DefectList):
    nextclosest = 0
    for key in coil_DefectList:
        defect = coil_DefectList[key]
        location = defect.location
        if location > 0:
            if location > closest:
                nextclosest = key

    return nextclosest


##
##return the total length of defects in current coil
def calc_total_fault_length(coil_DefectList):
    clean_Defects(coil_DefectList)
    total_defect_length = 0
    closest = get_ClosestDefect(coil_DefectList)
    if debugPrint:
        print('calc_total_fault_length closest =', closest)
    return coil_DefectList[closest].length


##add a pipe to the current cutlist
def add_to_cutlist(cutlist, pipelen, def_len):
    pipe = millvar.Pipe('XCUT', pipelen, def_len)
    if debugPrint:
        print('add cutlist: ', pipe)
    if pipelen < millvar.mill_Min_Length:
        raise ValueError(pipelen)
    if pipelen <= millvar.mill_Max_Length:
        cutlist.append(pipe)
        if debugPrint:
            print(str(pipe.length) + " added to cutlist with " + str(pipe.defect_length) + " defect")
    else:
        raise ValueError(pipelen)


    return cutlist


def remove_defect(coil_DefectList, location):
    if debugPrint:
        print('remove defect', location)
    newdefects = []

    for key in coil_DefectList:
        defect = coil_DefectList[key]
        dLoc = defect.location
        dLen = defect.length
        dType = defect.defect_type
        oldDefect = millvar.Defect(dLoc, dLen, dType)
        if key != location:
            newdefects.append(oldDefect)




            # Clear coil defect list before we rewrite it with updated information
    coil_DefectList.clear()
    # Rewrite defect list to reflect mill movement
    for defect in newdefects:
        defectid = int(defect.location)
        if defectid > 0:
            coil_DefectList[defectid] = defect

    return coil_DefectList


def add_defect(coil_DefectList, location, length, dtype):
    newdefects = []
    new_defect = millvar.Defect(location, length, dtype)

    for key in coil_DefectList:
        defect = coil_DefectList[key]
        dLoc = defect.location
        dLen = defect.length
        dType = defect.defect_type
        oldDefect = millvar.Defect(dLoc, dLen, dType)
        newdefects.append(oldDefect)
    newdefects.append(new_defect)

    # Clear coil defect list before we rewrite it with updated information
    coil_DefectList.clear()
    # Rewrite defect list to reflect mill movement
    for defect in newdefects:
        defectid = int(defect.location)
        if defectid > 0:
            coil_DefectList[defectid] = defect

    return coil_DefectList


def shift_defect(coil_DefectList, offset):
    newdefects = []

    for key in coil_DefectList:
        defect = coil_DefectList[key]
        dLoc = defect.location + offset
        dLen = defect.length
        dType = defect.defect_type
        oldDefect = millvar.Defect(dLoc, dLen, dType)
        newdefects.append(oldDefect)

    # Clear coil defect list before we rewrite it with updated information
    coil_DefectList.clear()
    # Rewrite defect list to reflect mill movement
    for defect in newdefects:
        defectid = int(defect.location)
        if defectid > 0:
            coil_DefectList[defectid] = defect

    return coil_DefectList


def evaluate_pipes(pipelist, coillist):
    pipecount = 0
    pipelength = 0
    pipelen = 0
    wholescraplength = 0
    wholescrapcount = 0
    scraplength = 0
    scrapcount = 0
    coillength = 0
    for coil in coillist:
        coillength += coil[0]
    #print('coilength = ', coillength)
    # print('\n')
    for pipes in pipelist:
        for pipe in pipes:
            pipelen = pipe[1] - pipe[2]

            if pipelen >= millvar.mill_Min_Length:
                scraplength += pipe[2]
                pipecount += 1
                pipelength += pipelen
            else:
                scraplength += pipe[1]

    if debugPrint:
        print(pipe[0], ',', round(pipe[1], 1), ',', round(pipe[2], 1))

    if debugPrint:
        print('Evaluate Pipes - total pipe length = ', round(pipelength, 2), coillength)
        print('Evaluate Pipes - scraplength = ', scraplength)
        print('Evaluate Pipes - Yield = ', round(pipelength / coillength, 3))
    return (coillength, round(pipelength, 2), pipecount, scraplength,round(pipelength / coillength, 3))


def add_millstop_thiscoil(coil_DefectList, tco_pipelength, thiscut, thisdefectlength, cutlist):
    #coil_DefectList = add_defect(coil_DefectList, 153, millvar.millStop_BadLength, 3)
    closest = get_ClosestDefect(coil_DefectList)
    result = []
    newcutlist = []
    new_defectlist=[]
    add_to_cutlist(newcutlist,thiscut,thisdefectlength)
    if debugPrint:
        pass
        print('add mill stop this coil')
        print ('old and new cutlist',cutlist)
        print(newcutlist)
    left_to_finish = thiscut - tco_pipelength
    cutnow = False

    if debugPrint:
        pass
        print('add mill stop - left to finish= ',left_to_finish)
        print('closest:', closest)
        print('start millstop defect list = ', coil_DefectList)
        print('tco pipelength', tco_pipelength)
    coil_DefectList = add_defect(coil_DefectList, 153 , millvar.millStop_BadLength, 3)
    closest = get_ClosestDefect(coil_DefectList)
    if debugPrint:
        pass
        print('Add Stop defect')
        print('closest:', closest)
        print('new millstop defect list = ', coil_DefectList)
        print('tco pipelength', tco_pipelength)
        print('Updated defectlist = ',coil_DefectList)
    # if tco_pipelength > 0: #millvar.mill_Min_Length :  set to 0 so we never really make the choice
    finish_cut = True

    if get_coil_length(coil_DefectList) < 153:
        pass
        if debugPrint:
            print('Mill stop affects this coil so this should never happen')
        exit()
    # defect on next coil
    else:

        if debugPrint:
            print('closest defect =', closest)
            #print('old defect = ', )
            print('current TCO Length = ', tco_pipelength)
            print('Current defect List', coil_DefectList)
            print('original cut =', thiscut)
            print('Original cutlist = ', cutlist)

        coil_DefectList = shift_defect(coil_DefectList, -left_to_finish)
        newcutlist = optimize(coil_DefectList)
        if debugPrint:
            print('new cutlist = ', newcutlist)
            print('mill stop optimize')

    newcutlist=['XCUT',thiscut,thisdefectlength]
    if debugPrint:
        print ('coil_DefectList, newcutlist, thiscut', coil_DefectList, newcutlist, thiscut)
    result = [cutnow, coil_DefectList, newcutlist, thiscut]

    return result


def rich_optimize(coil_DefectList):
    #New Optimization Algorithm that seeks to maximize length average rather than coil yield
    cutlist = []
    if millvar.crush_test == True:
        crushtest_length = millvar.crushtest_length
    else:
        crushtest_length = 0.0

    CAPL = 0.0
    current_coil_length = get_coil_length(coil_DefectList)
    if debugPrint:
        print('\nStart rich Optimize with current coil length:', current_coil_length)
        print(coil_DefectList)
    if len(coil_DefectList) == 0:
        return cutlist
        raise ValueError('zero length coil DefectList')
    closest = get_ClosestDefect(coil_DefectList)
    steel_remain = coil_DefectList[closest]
    defect_length = steel_remain.length
    defect_Type = steel_remain.defect_type
    available_steel = steel_remain.location
    if debugPrint:
        print('Optimize parameters:', closest, steel_remain, defect_length, defect_Type, available_steel)
    next_closest = get_Next_Closest_Defect(available_steel, coil_DefectList)
    if debugPrint:
        print('next closest', next_closest)
    if next_closest > 0:
        next_Remain = coil_DefectList[next_closest]
        next_defect_length = next_Remain.length
        next_defect_Type = next_Remain.defect_type
        next_available_steel = next_Remain.location
    else:
        next_Remain = steel_remain
        next_defect_length = defect_length
        next_defect_Type = defect_Type
        next_available_steel = available_steel
    if debugPrint:
        print('closest defect :', steel_remain.location, steel_remain.length)
        print('next defect :', next_Remain.location, next_defect_length)
        print('optimize defect length =', defect_length)

    CAPL = available_steel * 1.0  - defect_length
    if CAPL < millvar.mill_Min_Length and millvar.hold_defect:
        if next_available_steel >= millvar.mill_Min_Length:
            CAPL = next_available_steel
        else:
            print ('Doh!')
    if debugPrint:
        print('CAPL=', CAPL, 'crushtest_length=', crushtest_length, 'defect length', defect_length)
    CAPL = CAPL - crushtest_length
    if debugPrint:
        print('CAPL=', CAPL)
    NAPL = next_available_steel * 1.0  # - next_defect_length
    if debugPrint:
        print('NAPL=', NAPL)

    ## = CAPL
    # How many max length pieces can we get from CAPL took from CAPL- defect_length
    K_max_num_pieces = int((CAPL) / millvar.max_Length)
    if K_max_num_pieces == 0:
        if debugPrint:
            print('Can not cut a max length pipe')
    tail = CAPL - (K_max_num_pieces * millvar.max_Length)


    if debugPrint:
        print ('K, CAPL, Tail = ',K_max_num_pieces,CAPL,tail)
        print('we can add ',K_max_num_pieces,' max length to cutlst')

    if tail +2*defect_length <= millvar.mill_Max_Length:
        # If Tail + defect <= mill maximum length we check more otherwise we know that
        # we probably have a large tail with large defect
        if debugPrint:
            print('tail +2* defect <= mill Max Len')
        if tail+2*defect_length >= millvar.mill_Min_Length:
            # if the Tail and defect can be cut and are long enough (>= mill minimum length)
            # we can cut K max legth pieces and then deal with the tail and defect otherwise we
            # need to borrow from previous pipe
            if debugPrint:
                print('tail+2*defect >= mill mimimum')
            for i in range(0, K_max_num_pieces):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0

            add_to_cutlist(cutlist,tail+2*defect_length,2*defect_length)
            millvar.coil_pipe_number += 1

        else:
            # tail + defect does not meet minimum length to get through mill.  Need to
            #borrow from next pipe to get a minimum length pipe to fit through mill
            if debugPrint:
                print ('need to borrow get a minimum length')

            #calculate how much we need to borrow

                borrow = (millvar.mill_Min_Length-(tail+2*defect_length))
            if debugPrint:
                pass
                print('borrow =',borrow)

            for i in range(0, K_max_num_pieces):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0
            #we are borrowing from next coil to get a minimum length pipe now
            #since there is a defect in the middle of a minimum length pipe we count it as scrap
            #as there is no way it can contain a prime pipe
            add_to_cutlist(cutlist, millvar.mill_Min_Length, millvar.mill_Min_Length)
            millvar.coil_pipe_number += 1


    else:
        # Large Tail and large defect Check to see if defect is big enough to be won pipe
        if 2*defect_length >= millvar.mill_Min_Length:
            # the defect is large enough to be its own pipe
            if debugPrint:
                print('2 *defect >= Millvar.min length')
            for i in range(0, K_max_num_pieces-1):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0
            add_to_cutlist(cutlist,tail,0)
            millvar.coil_pipe_number += 1
            add_to_cutlist(cutlist,2*defect_length,2*defect_length)
            millvar.coil_pipe_number += 1
        else:
            # The defect isn't long enough to be won pipe but we can borrow from the tail
            # since the tail is so long if we got to this logic
            if debugPrint:
                print('need to borrow from tail')
                print(CAPL, tail)
            borrow = millvar.mill_Min_Length - 2*defect_length
            if debugPrint:
                print ('borrow:',borrow)
            for i in range(0, K_max_num_pieces):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0
            add_to_cutlist(cutlist,tail-borrow,0)
            millvar.coil_pipe_number += 1
            add_to_cutlist(cutlist,millvar.mill_Min_Length,millvar.mill_Min_Length)
            millvar.coil_pipe_number += 1

    return cutlist


def rich_optimize2(coil_DefectList):
    #New Optimization Algorithm that seeks to maximize length average rather than coil yield
    cutlist = []
    if millvar.crush_test == True:
        crushtest_length = millvar.crushtest_length
    else:
        crushtest_length = 0.0

    CAPL = 0.0
    current_coil_length = get_coil_length(coil_DefectList)
    if debugPrint:
        print('\nStart rich Optimize with current coil length:', current_coil_length)
        print(coil_DefectList)
    if len(coil_DefectList) == 0:
        return cutlist
        raise ValueError('zero length coil DefectList')
    closest = get_ClosestDefect(coil_DefectList)
    steel_remain = coil_DefectList[closest]
    defect_length = steel_remain.length
    defect_Type = steel_remain.defect_type
    available_steel = steel_remain.location
    if debugPrint:
        print('Optimize parameters:', closest, steel_remain, defect_length, defect_Type, available_steel)
    next_closest = get_Next_Closest_Defect(available_steel, coil_DefectList)
    if debugPrint:
        print('next closest', next_closest)
    if next_closest > 0:
        next_Remain = coil_DefectList[next_closest]
        next_defect_length = next_Remain.length
        next_defect_Type = next_Remain.defect_type
        next_available_steel = next_Remain.location
    else:
        next_Remain = steel_remain
        next_defect_length = defect_length
        next_defect_Type = defect_Type
        next_available_steel = available_steel
    if debugPrint:
        print('closest defect :', steel_remain.location, steel_remain.length)
        print('next defect :', next_Remain.location, next_defect_length)
        print('optimize defect length =', defect_length)

    CAPL = available_steel * 1.0  - defect_length
    if CAPL < millvar.mill_Min_Length and millvar.hold_defect:
        if next_available_steel >= millvar.mill_Min_Length:
            CAPL = next_available_steel
        else:
            print ('Doh!')
    if debugPrint:
        print('CAPL=', CAPL, 'crushtest_length=', crushtest_length, 'defect length', defect_length)
    CAPL = CAPL - crushtest_length
    if debugPrint:
        print('CAPL=', CAPL)
    NAPL = next_available_steel * 1.0  # - next_defect_length
    if debugPrint:
        print('NAPL=', NAPL)

    ## = CAPL
    # How many max length pieces can we get from CAPL took from CAPL- defect_length
    K_max_num_pieces = int((CAPL) / millvar.max_Length)
    if K_max_num_pieces == 0:
        if debugPrint:
            print('Can not cut a max length pipe')
    tail = CAPL - (K_max_num_pieces * millvar.max_Length)


    if debugPrint:
        print ('K, CAPL, Tail = ',K_max_num_pieces,CAPL,tail)
        print('we can add ',K_max_num_pieces,' max length to cutlst')

    if tail +2*defect_length <= millvar.mill_Max_Length:
        # If Tail + defect <= mill maximum length we check more otherwise we know that
        # we probably have a large tail with large defect
        if debugPrint:
            print('tail +2* defect <= mill Max Len')
        if tail+2*defect_length >= millvar.mill_Min_Length:
            # if the Tail and defect can be cut and are long enough (>= mill minimum length)
            # we can cut K max legth pieces and then deal with the tail and defect otherwise we
            # need to borrow from previous pipe
            if debugPrint:
                print('tail+2*defect >= mill mimimum')
            for i in range(0, K_max_num_pieces):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0
            if tail >= millvar.mill_Min_Length:
                #tail + defect?
                if debugPrint:
                    pass
                    print('ok tail >= mill min length')
                    print(tail+2*defect_length,2*defect_length)
                add_to_cutlist(cutlist,tail+2*defect_length,2*defect_length)
                millvar.coil_pipe_number += 1
            else:
                if debugPrint:
                    pass
                    print('ok tail < mill min length')
                    print(millvar.mill_Min_Length,2*defect_length)
                add_to_cutlist(cutlist, millvar.mill_Min_Length, 2 * defect_length)
                millvar.coil_pipe_number += 1
        else:
            # tail + defect does not meet minimum length to get through mill.  Need to borrow from
            # previous pipe to make minimum length to pass through mill
            if debugPrint:
                print ('need to borrow from a max to get a min')

            #calculate how much we need to take from previous pipe to make minimum length
            borrow = (millvar.mill_Min_Length-(tail+2*defect_length))
            if debugPrint:
                pass
                print('borrow from previous =',borrow)
            #since we borowed we can only make K-1 max length pipes
            for i in range(0, K_max_num_pieces-1):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0

            if millvar.max_Length-borrow >= millvar.mill_Min_Length:
                #this is necessary for max lengths < 80
                if debugPrint:
                    pass
                    print('good borrow')
                add_to_cutlist(cutlist,millvar.max_Length-borrow,0)
                millvar.coil_pipe_number += 1
                add_to_cutlist(cutlist, millvar.mill_Min_Length, 2*defect_length)
                millvar.coil_pipe_number += 1
            else:
                # This means that I need to borrow from the next pipe too.  So we will just create two
                # minimum length pipes.
                if debugPrint:
                    pass
                    print("I'm here in unable to borrow from only one pipe cutting two min length instead")
                add_to_cutlist(cutlist,millvar.mill_Min_Length,0)
                millvar.coil_pipe_number += 1
                add_to_cutlist(cutlist,millvar.mill_Min_Length,2*defect_length)
                millvar.coil_pipe_number += 1

    else:
        # Large Tail and large defect Check to see if defect is big enough to be won pipe
        if 2*defect_length >= millvar.mill_Min_Length:
            # the defect is large enough to be its own pipe
            if debugPrint:
                print('2 *defect >= Millvar.min length')
            for i in range(0, K_max_num_pieces-1):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0
            add_to_cutlist(cutlist,tail,0)
            millvar.coil_pipe_number += 1
            add_to_cutlist(cutlist,2*defect_length,2*defect_length)
            millvar.coil_pipe_number += 1
        else:
            # The defect isn't long enough to be won pipe but we can borrow from the tail
            # since the tail is so long if we got to this logic
            if debugPrint:
                print('need to borrow from tail')
                print(CAPL, tail)
            borrow = millvar.mill_Min_Length - 2*defect_length
            if debugPrint:
                print ('borrow:',borrow)
            for i in range(0, K_max_num_pieces):
                add_to_cutlist(cutlist, millvar.max_Length + crushtest_length, crushtest_length)
                millvar.coil_pipe_number += 1
                crushtest_length = 0
            add_to_cutlist(cutlist,tail-borrow,0)
            millvar.coil_pipe_number += 1
            add_to_cutlist(cutlist,millvar.mill_Min_Length,millvar.mill_Min_Length)
            millvar.coil_pipe_number += 1

    return cutlist



# optimization
# This attempts to replicate the cut optimization logic as described in the functional spec
# and documented by the flowcharts.
# In other words, this is where the magic happens
# the input parameter coil_DefectList is a list of defects that that are defined in millvar.py as :
#   Defect=collections.namedtuple("Defect",["location","length","defect_type"])
#   each defect has a location from the head, a length, and a type
#       type 1 is a crossweld
#       type 2 is a furnace tear specified from the steel mill
#       type 3 is a mill stop
# The funtion returns a list of pipes as cutlist where a pipe is defined in millvar as:
# Pipe = collections.namedtuple("Pipe",["pipeid","length","defect_length"])
def optimize(coil_DefectList):
    cutlist =[]
    #print (coil_DefectList)
    coil_DefectList = clean_Defects(coil_DefectList)
    if millvar.crush_test == True:
        crushtest_length = millvar.crushtest_length
    else:
        crushtest_length = 0.0
    if richOptimize:
        #Use new average length maximizing algorithm
        cutlist = rich_optimize(coil_DefectList)
    else:
        #Use Original Brock Optimization Algorithm
        CAPL = 0.0
        NAPL = 0.0
        neg_tcount = 0
        current_coil_length = get_coil_length(coil_DefectList)
        if debugPrint:
            print('\nStart Optimize with current coil length:', current_coil_length)
            print(coil_DefectList)

        # see previous cutlist for debugging purposes
        # print('cutlist before optimize', millvar.cutlist)

        # Clear cutlist
        cutlist = []
        if len(coil_DefectList) == 0:
            return cutlist
            raise ValueError('zero length coil DefectList')
        closest = get_ClosestDefect(coil_DefectList)
        steel_remain = coil_DefectList[closest]
        defect_length = steel_remain.length
        defect_Type = steel_remain.defect_type
        available_steel = steel_remain.location
        if debugPrint:
            print('Optimize parameters:', closest, steel_remain, defect_length, defect_Type, available_steel)
        next_closest = get_Next_Closest_Defect(available_steel, coil_DefectList)
        if debugPrint:
            print('next closest', next_closest)
        if next_closest > 0:
            next_Remain = coil_DefectList[next_closest]
            next_defect_length = next_Remain.length
            next_defect_Type = next_Remain.defect_type
            next_available_steel = next_Remain.location
        else:
            next_Remain = steel_remain
            next_defect_length = defect_length
            next_defect_Type = defect_Type
            next_available_steel = available_steel
        if debugPrint:
            print('closest defect :', steel_remain.location, steel_remain.length)
            print('next defect :', next_Remain.location, next_defect_length)

            # fault_length = calc_total_fault_length(coil_DefectList)
            # if debugPrint:
            #     print('length of closest fault = ', fault_length)


            # Calculate Current Available Prime Length

            if debugPrint:
                print('optimize defect length =', defect_length)

        CAPL = available_steel * 1.0   - defect_length
        if CAPL < millvar.mill_Min_Length and millvar.hold_defect:
            if next_available_steel >= CAPL:
                CAPL = next_available_steel
            else:
                print ('Huh')
        if debugPrint:
            print('CAPL=', CAPL, 'crushtest_length=', crushtest_length, 'defect length', defect_length)
        CAPL = CAPL - crushtest_length  # - defect_length #-millvar.crossweld_BadLength
        if debugPrint:
            print('CAPL=', CAPL,' test length =',crushtest_length)
        NAPL = next_available_steel * 1.0  - next_defect_length
        if debugPrint:
            print('NAPL=', NAPL)

        ## = CAPL
        # How many max length pieces can we get from CAPL took from capl- defect_length
        K_max_num_pieces = int((CAPL) / millvar.max_Length)
        if K_max_num_pieces == 0:
            K_max_num_pieces = int(CAPL / millvar.max_Length)

        tail_Length = CAPL - (K_max_num_pieces * millvar.max_Length)  # - defect_length

        if debugPrint:
            print('CAPL: ', CAPL, ' K: ', K_max_num_pieces, 'tail: ', tail_Length, ' defect length: ', defect_length,
                  ' test length:', crushtest_length)

        if K_max_num_pieces > 0:
            if debugPrint:
                print('K > 0')
            if tail_Length >= millvar.alt_Minimum_Length:
                # PLC Long Tail Page
                if debugPrint:
                    print('tail > altmin - Long Tail', tail_Length)
                if tail_Length + 2 * defect_length + crushtest_length > millvar.mill_Max_Length:
                    # PLC Long Tail
                    if debugPrint:
                        print('Long Tail')
                    for i in range(0, int(K_max_num_pieces)):
                        # cut K pipes of max length 1 with tail + test and defect will go on next pipe
                        if debugPrint:
                            print('Long tail -add Max Length to cutlist ', millvar.max_Length)
                        #add_to_cutlist(cutlist, millvar.max_Length+crushtest_length, crushtest_length)
                        add_to_cutlist(cutlist, millvar.max_Length ,millvar.hold_defect_length)
                        millvar.crush_test = False
                        millvar.hold_defect_length=0
                        millvar.coil_pipe_number += 1
                        if debugPrint:
                            print(millvar.max_Length, 0)
                            print('CT Long Tail @ max length with crushtest: ', millvar.max_Length + crushtest_length, i)
                        ## -= millvar.max_Length
                        # crushtest_length= 0.0
                        ##pipe_steel -= (millvar.max_Length+crushtest_length)

                    if debugPrint:
                        print('Long tail add tail plus crushtest to cutlist ', tail_Length, crushtest_length)
                    add_to_cutlist(cutlist, tail_Length + crushtest_length, crushtest_length)
                    crushtest_length=0
                    millvar.crush_test = False
                    millvar.coil_pipe_number += 1
                    if debugPrint:
                        print(millvar.mill_Max_Length, 0)
                        print('CT Long Tail @ max length: ', millvar.max_Length + crushtest_length, i)
                    ##pipe_steel -= (millvar.max_Length + crushtest_length)


                    if debugPrint:
                        print('Long Tail - add tail - leave defect for next pipe ', round(crushtest_length, 1))
                    crushtest_length = 0.0
                    millvar.hold_defect = True
                    if defect_length >=  millvar.millStop_BadLength:
                        if debugPrint:
                            print('add millstop pipe to cutlist')
                        add_to_cutlist(cutlist,2* millvar.millStop_BadLength,2* millvar.millStop_BadLength)
                        millvar.coil_pipe_number += 1
                    else:
                        if debugPrint:
                            pass
                            print('hold defect for next pipe or coil')
                        #add_to_cutlist(cutlist,2*defect_length,2*defect_length)
                        millvar.hold_defect = True
                        millvar.hold_defect_length = defect_length
                        millvar.hold_defect_type = defect_Type

                    # print('Long Tail add tail and test: ', round(millvar.mill_Min_Length, 1))
                    # pipe_steel -= tail_Length + defect_length + crushtest_length


                else:
                    # long tail but not too long
                    # cut K of max length and the last pipe with tail+test+defect
                    if debugPrint:
                        print('Long Tail but not too long', crushtest_length)
                    for i in range(0, int(K_max_num_pieces)):
                        if debugPrint:
                            print('Long tail but not too long  - tail < mill max - add max length to cutlist')
                        add_to_cutlist(cutlist, millvar.max_Length+crushtest_length, millvar.hold_defect_length)
                        millvar.hold_defect_length=0
                        millvar.crush_test = False
                        ##pipe_steel -= (millvar.max_Length+crushtest_length)
                        millvar.coil_pipe_number += 1
                        crushtest_length = 0.0
                        if debugPrint:
                            print('max Length plus crushtest')  # do crushtest pipe

                    if debugPrint:
                        print(millvar.max_Length)
                        print('2CT Long Tail @ max length,crushtest length: ', millvar.max_Length + crushtest_length, i)

                    add_to_cutlist(cutlist, round(tail_Length + 2 * defect_length + crushtest_length, 1),
                                   2 * defect_length + crushtest_length)
                    millvar.coil_pipe_number += 1

                    ##pipe_steel -= round(tail_Length + 2*defect_length+crushtest_length)
                    if debugPrint:
                        print('Long Tail OK - tail + defects and test: ',
                              round(tail_Length + 2 * defect_length + crushtest_length, 1))

                    crushtest_length = 0.0
                    millvar.crush_test = False



            else:
                if debugPrint:
                    print("PLC Main 2 Tail < alt_min ", tail_Length)
                # if tail_Length+2*defect_length > millvar.mill_Min_Length:
                #     print('think we have mill stop pipe so treat special')
                #     add_to_cutlist(cutlist,tail_Length+2*defect_length,tail_Length+2*defect_length)
                #
                P_max_len_pipes = int( math.ceil(
                    (millvar.alt_Minimum_Length - tail_Length) / (millvar.max_Length - millvar.alt_Minimum_Length)))
                if debugPrint:
                    print('P=', P_max_len_pipes)

                if debugPrint:
                    print('P= ', P_max_len_pipes, 'K= ', K_max_num_pieces, 'Tail = ', tail_Length)

                if P_max_len_pipes > K_max_num_pieces:
                    # P>K
                    # Do the logic on PLC Short CAPL
                    if debugPrint:
                        print(" P > K :Short CAPL")
                    N_num_Alt_Min_Pipes = int(CAPL / millvar.alt_Minimum_Length)
                    if debugPrint:
                        print('N = ', N_num_Alt_Min_Pipes)

                    tail_Length2 = CAPL - (N_num_Alt_Min_Pipes * millvar.alt_Minimum_Length)
                    if debugPrint:
                        print("tail 2=" + str(tail_Length2) + " defect = " + str(defect_length))

                    if tail_Length2 >= millvar.mill_Min_Length:
                        if debugPrint:
                            print('tail2 >= mill min add alt min to cutlist', millvar.alt_Minimum_Length)
                        # Cut N pipes wiith Alt_Min Length and last pipe with Tail2+Fault+Test
                        for i in range(0, N_num_Alt_Min_Pipes):
                            if debugPrint:
                                print('tail2 >= mill min add alt min to cutlist', millvar.alt_Minimum_Length)
                            add_to_cutlist(cutlist, round(millvar.alt_Minimum_Length, 1), 0)
                            millvar.coil_pipe_number += 1
                            ##pipe_steel -= millvar.alt_Minimum_Length
                            # print('prime remaining:', pipe_steel)

                        if tail_Length2 + 2 * defect_length + crushtest_length <= millvar.mill_Max_Length:
                            if debugPrint:
                                print('tail2 >= mill min add tail+defect+test to cutlist',
                                      round(tail_Length2 + 2 * defect_length + crushtest_length))

                            add_to_cutlist(cutlist, round(tail_Length2 + 2 * defect_length + crushtest_length, 1),
                                           2 * defect_length+crushtest_length)
                            millvar.coil_pipe_number += 1
                            crushtest_length = 0.0
                            # print('prime remaining:', pipe_steel)
                        else:
                            if debugPrint:
                                print('tail2 + defect > mill max length   add tail keep rest for next pipe', tail_Length2)
                            if defect_length >= millvar.millStop_BadLength:
                                if debugPrint:
                                    print('defect is mill stop - create full scrap')
                                add_to_cutlist(cutlist, round(tail_Length2, 1), 0)
                                millvar.coil_pipe_number += 1
                                add_to_cutlist(cutlist,2*defect_length,2*defect_length)
                                millvar.coil_pipe_number += 1
                            else:
                                print ('OK defect is not mill stop')
                                add_to_cutlist(cutlist, round(tail_Length2, 1), 0)
                            ##pipe_steel -= tail_Length2
                                millvar.coil_pipe_number += 1
                            # print('prime remaining:', pipe_steel)
                                millvar.crush_test = False
                                millvar.hold_defect = True
                                millvar.hold_defect_length = defect_length
                                millvar.hold_defect_type = defect_Type
                                crushtest_length = 0
                    else:
                        if debugPrint:
                            print('tail2 < mill minimum')
                        # Add 1 pipe of max length then n-1 with alt minimum then attach tail 3 +defects to last alt min pipe
                        tail_Length3 = tail_Length2 + millvar.alt_Minimum_Length - millvar.max_Length
                        if debugPrint:
                            print('tail 3 = ', tail_Length3)
                        if debugPrint:
                            print('tail2 < mill min add max to cutlist')
                        add_to_cutlist(cutlist, millvar.max_Length, 0)
                        millvar.coil_pipe_number += 1
                        # print('prime remaining:', pipe_steel)
                        for i in range(0, N_num_Alt_Min_Pipes - 2):
                            if debugPrint:
                                print('add alt min to cutlist')
                            add_to_cutlist(cutlist, millvar.alt_Minimum_Length, 0)
                            millvar.coil_pipe_number += 1
                            # print('prime remaining:', pipe_steel)
                        if tail_Length3 >= 0:
                            # RMCheck - need to verify next line of logic
                            # add_to_cutlist(cutlist, millvar.alt_Minimum_Length+round(tail_Length3 + 2*defect_length+crushtest_length, 1), 2*defect_length+crushtest_length)
                            # print('Boom')
                            if 2 * defect_length+tail_Length3+crushtest_length >= millvar.mill_Min_Length:
                                if debugPrint:
                                    print('add millstop pipe from tail3')

                                add_to_cutlist(cutlist, round(tail_Length3 + 2 * defect_length + crushtest_length, 1),
                                               2 * defect_length + crushtest_length)
                            else:
                                #print('Boom')
                                #add_to_cutlist(cutlist, millvar.mill_Min_Length + round(
                                 #   tail_Length3 + 2 * defect_length + crushtest_length, 1),
                                 #              2 * defect_length + crushtest_length)
                                add_to_cutlist(cutlist, millvar.mill_Min_Length ,
                                               millvar.mill_Min_Length)
                            millvar.coil_pipe_number += 1
                        else:
                            print('tail3 < 0')
                            #exit()

                        millvar.crush_test = False
                        crushtest_length = 0
                else:
                    # P<=K
                    # Rich
                    if debugPrint:
                        ('test=', millvar.crush_test, crushtest_length)
                    if debugPrint:
                        print('P <= K ;P_max_len_pipes = ', P_max_len_pipes, ' tail=', tail_Length)

                    if P_max_len_pipes > 0:
                        if debugPrint:
                            print(tail_Length, P_max_len_pipes * millvar.max_Length, millvar.alt_Minimum_Length,
                                  P_max_len_pipes)
                        secondary_Length = ((tail_Length +
                                             (
                                             P_max_len_pipes * millvar.max_Length) - millvar.alt_Minimum_Length) / P_max_len_pipes)
                        if debugPrint:
                            print('secondary_Length', secondary_Length)
                            print('K:', K_max_num_pieces)
                            print('P:', P_max_len_pipes)
                    else:
                        print('P=0')
                        exit()
                    for i in range(0, K_max_num_pieces - P_max_len_pipes):
                        add_to_cutlist(cutlist, millvar.max_Length+crushtest_length, crushtest_length)
                        millvar.crush_test = False
                        crushtest_length = 0
                        millvar.coil_pipe_number += 1
                        if debugPrint:
                            print('add max', i)
                    for i in range(0, P_max_len_pipes):
                        add_to_cutlist(cutlist, round(secondary_Length, 1), 0)
                        ##pipe_steel -= round(secondary_Length, 1)
                        millvar.coil_pipe_number += 1
                        if debugPrint:
                            print('add secondary', secondary_Length, i)
                            print('culprit 2 = ', 2 * defect_length + crushtest_length)
                    addme = millvar.alt_Minimum_Length + 2 * defect_length + crushtest_length
                    if debugPrint:
                        print('addme =',addme)
                    if addme > millvar.mill_Max_Length:
                        if debugPrint:
                            print('uh oh', addme)
                        addme = millvar.mill_Min_Length + 2 * defect_length + crushtest_length
                    if addme > millvar.mill_Max_Length:
                        if debugPrint:
                            print('double uh oh', addme)
                        addme = millvar.mill_Min_Length + 2 * defect_length

                    if addme > millvar.mill_Max_Length:
                        if debugPrint:
                            print('triple uh oh', addme)
                    add_to_cutlist(cutlist, addme, 2 * defect_length + crushtest_length)
                    millvar.coil_pipe_number += 1

                    if debugPrint:
                        print('add Alt minimum +defect+test after secondary'
                              ,millvar.alt_Minimum_Length + 2 * defect_length + crushtest_length)
                    millvar.crush_test = False
                    crushtest_length = 0
                    # end indent
        else:
            if debugPrint:
                print('K <=0 PLC Main Algorithm #2')
                print('CAPL:', CAPL, 'defect length', defect_length, 'test length', crushtest_length)
            if CAPL < millvar.mill_Min_Length:
                if debugPrint:
                    print('Short CAPL2')


            if tail_Length + 2 * defect_length + crushtest_length >= millvar.mill_Min_Length:
                if debugPrint:
                    print('tail_Length + 2 * defect_length + crushtest_length >= millvar.mill_Min_Length')
                if tail_Length + 2 * defect_length + crushtest_length > millvar.mill_Max_Length:

                    if defect_length >=millvar.millStop_BadLength:
                        add_to_cutlist(cutlist, round(tail_Length + crushtest_length, 1), 2*millvar.millStop_BadLength+crushtest_length)
                    else:
                        add_to_cutlist(cutlist, round(tail_Length + crushtest_length, 1), crushtest_length)
                    ##pipe_steel -= round(tail_Length+crushtest_length, 1)
                    millvar.coil_pipe_number += 1
                    if debugPrint:
                        print('too much. defect on next pipe')

                    # print('prime remaining:', pipe_steel)
                    millvar.crush_test = False
                    crushtest_length = 0
                    millvar.hold_defect = True
                    millvar.hold_defect_length = defect_length
                    millvar.hold_defect_type = defect_Type
                    pass
                else:
                    if millvar.hold_defect_length >= millvar.millStop_BadLength:
                        add_to_cutlist(cutlist, 2 * millvar.hold_defect_length,
                                       2 * millvar.hold_defect_length )
                        millvar.hold_defect_length = 0
                        millvar.hold_defect_type = 0
                        millvar.hold_defect = False
                    else:
                        if debugPrint:
                            print('Rich')
                        add_to_cutlist(cutlist, tail_Length + 2 * defect_length + crushtest_length,
                                   2 * defect_length + crushtest_length)
                    millvar.coil_pipe_number += 1
            else:
                if debugPrint:
                    print('cut min length')
                add_to_cutlist(cutlist, millvar.mill_Min_Length, 2 * defect_length)
                ##pipe_steel -= millvar.mill_Min_Length
                millvar.coil_pipe_number += 1

                # print ('prime remaining:',pipe_steel)
                # millvar.newfault = 0
                # return cutlist
                millvar.crush_test = False
                crushtest_length = 0


                # print('prime remaining:', pipe_steel)

                # millvar.newfault = 0
                # return cutlist
                # add_front = CAPL

    cut_pipes_total = 0  # coil_DefectList = remove_defect(coil_DefectList, steel_remain)
    for cut in cutlist:
        cut_pipes_total += cut[1]

    # if debugPrint:
    #     print('Total of pipe cut from coil:', cut_pipes_total)
    #     print('coil start:', current_coil_length)
    return cutlist


############################################################
#  run_1_unit is called to simulate 1 unit  of mill travel
#  there is a probability that there will be a mill stop
#  this is represented as # of stops per 10000 feet
#
# This updates the defect list to simulate 1 foot of mill movement
# pipe length and coil movement are handled elsewhere
#
#############################################################
def run_1_unit(coil_DefectList):
    # print('run 1 ft ',coil_DefectList)
    # prepare for updated defect list
    newdefects = []
    nextCoilDefects = []
    # millstop = 0

    # decrement defect footage counts and create new defect list
    for key in coil_DefectList:
        defect = coil_DefectList[key]
        dLoc = round(defect.location - millvar.simulation_step, 1)
        dLen = defect.length
        dType = defect.defect_type
        if dLoc > 0:
            newdefect = millvar.Defect(dLoc, dLen, dType)
            newdefects.append(newdefect)

    # Clear coil defect list before we rewrite it with updated information
    coil_DefectList.clear()
    # Rewrite defect list to reflect mill movement
    for defect in newdefects:
        defectid = int(defect.location)
        if defectid > 0:
            coil_DefectList[defectid] = defect

    return coil_DefectList





def run_coil(coil, coil_num, headChop, millstop_carry):
    brock_factor = -153.0
    reoptimize = False
    cutnow = False
    #millvar.hold_defect = False



    coil_pipelength = 0.0
    if headChop > 1:
        millvar.hold_defect=True
        millvar.hold_defect_type = 1
        millvar.hold_defect_length = millvar.crossweld_BadLength
        if debugPrint:
            pass
            print('headchop >0 ', headChop)
            print ('Previous Coil Leftover, hold defect, coil number',headChop,millvar.hold_defect,coil_num)

    if debugPrint:
        print('Enter run_coil ', coil, headChop)
        print('Coil num, millstop_carry', coil_num, millstop_carry)

    static_millStop = coil[4]  # +brock_factor # Get static mill stop point
    if static_millStop > 0:

        if debugPrint:
            ('static millstop is at', static_millStop)

    if static_millStop == 0:
        static_millStop = -1000

    tco_PipeLength = 0.0
    pipe_count = 0
    num_of_mill_stops = 0
    newpipes = []
    newfault = 0
    millvar.crush_test = True
    if debugPrint:
        print('load coil:', coil, 'Crushtest=', millvar.crush_test)
    # set initial defect list for the coil and subtract crossweld and deficit from previous coil if present

    coil_DefectList = load_Coil(coil, headChop)
    if millvar.hold_defect:
        #shift_defect(coil_DefectList,2*millvar.hold_defect_length)
        #remove_defect(coil_DefectList,int(2*millvar.hold_defect_length))
        if debugPrint:
            pass
            print('remove defect at hold defect')
        # add_defect(coil_DefectList,1,int(millvar.hold_defect_length),millvar.hold_defect_type)
        # millvar.hold_defect=False
        # millvar.hold_defect_length=0
        # millvar.hold_defect_type = 0
    coil_length = get_coil_length(coil_DefectList)
    running_Coil_Length = coil_length
    if debugPrint:
        print('new start length = ', coil_length)
    if debugPrint:
        print('preclean defects:', coil_DefectList)

    coil_DefectList = clean_Defects(coil_DefectList)  # clean up in case of negative from previous coil being removed
    if debugPrint:
        print('post clean defects and headchop:', coil_DefectList, headChop)
    if millstop_carry > 0:
        # coil_DefectList = add_defect(coil_DefectList, millstop_carry + headChop, millvar.millStop_BadLength, 3)
        coil_DefectList = add_defect(coil_DefectList, millstop_carry, millvar.millStop_BadLength, 3)
        if debugPrint:
            print(coil_DefectList)
            print('add millstop carry ', millstop_carry)
        exit()
        if debugPrint:
            print('rc defects', coil_DefectList, millstop_carry)
    millstop_carry = 0
    # Do first pass at optimization and get first cut list

    if len(coil_DefectList) != 0:
        if millvar.hold_defect:
            cutlist =[]
            add_to_cutlist(cutlist,millvar.max_Length,2*millvar.hold_defect_length)
            millvar.crushtest = False
            millvar.hold_defect = False
            millvar.hold_defect_length = 0
            millvar.hold_defect_type = 0
        else:
            cutlist = optimize(coil_DefectList)  # First Optimize the cuts
        if debugPrint:
            print('Running Coil Length:', running_Coil_Length)
            print('defect list\n', coil_DefectList)
            print('first cutlist\n', cutlist)

        closest = get_ClosestDefect(coil_DefectList)
        thisdefect = coil_DefectList[closest]
    # print('Initial cutlist   \n',cutlist)
    # print "fault length = ", fault_length


    pipe_number = 1

    # Run the coil until we run out
    if debugPrint:
        print('Start Running coil length: ', running_Coil_Length)
    while running_Coil_Length > millvar.mill_Min_Length: #0
        if cutnow == False:
            closest = get_ClosestDefect(coil_DefectList)
            if debugPrint:
                print('running coil, closest', running_Coil_Length, closest)
            thisdefect = coil_DefectList[closest]
            if debugPrint:
                print('current defect', thisdefect.location)
        if debugPrint:
            print('Loop running_coil_length', running_Coil_Length, 'Coil#:', coil_num, 'Pipe#:', pipe_number)
            print(get_coil_length(coil_DefectList))
        if len(cutlist) == 0 or newfault == 1:
            cutlist = []
            if debugPrint:
                print('empty cutlist')
                break
            cutlist = optimize(coil_DefectList)

            thiscut = cutlist[0].length
            thispipe = cutlist[0]
        for cut in cutlist:
            # RM if reoptimize == True:
            #     break
            if debugPrint:
                print('DEFECT LIST:', coil_DefectList)
            if debugPrint:
                print('cut= ', cut)
            thiscut = cut[1]
            thisdefectlength = cut[2]
            if debugPrint:
                print('Begin TCO cut')
                print('Pipe: ', pipe_number, 'cut = ', thiscut)

            while tco_PipeLength <= thiscut:
                # cutnow = False
                # run 1 unit of coil simulation
                # if debugPrint:
                #     print('call run_1_unit:', millvar.simulation_step,tco_PipeLength,'\n',coil_DefectList)
                coil_DefectList = run_1_unit(coil_DefectList)
                tco_PipeLength += millvar.simulation_step
                running_Coil_Length = round(get_coil_length(coil_DefectList), 1)

                # check for preset mill stop
                if static_millStop <= 0 or (coil_pipelength + tco_PipeLength) < static_millStop:
                    # print(coil_pipelength+tco_PipeLength)
                    # no stop so move on
                    pass
                else:
                    if static_millStop > 0:  # Add static mill stop if needed
                        newfault = 1

                # Done checking for staic mill stop
                # Check for random stop would go here

                # What do we do when a mill stop occurs?
                if newfault == 1:
                    defect_offset = 0
                    if debugPrint:
                        pass
                        print('*****Mill Stop******* at', running_Coil_Length, ' current pipe length = ',
                              tco_PipeLength, 'curent cut =', thiscut, 'running coil length:', running_Coil_Length)

                    # Decide if mill stop affects current coil or next coil

                    # mill stop affects current coil
                    newfault = 0
                    static_millStop = -10000
                    if running_Coil_Length > 153:

                        millvar.crush_test = True
                        # actions = add_millstop_thiscoil(coil_DefectList, tco_PipeLength,thiscut,thisdefect[2])
                        actions = add_millstop_thiscoil(coil_DefectList, tco_PipeLength, thiscut, thisdefect[2],
                                                        cutlist)
                        if debugPrint:
                            print('Actions',actions)
                        newfault = 0
                        cutnow = actions[0]
                        coil_DefectList = actions[1]
                        cutlist = actions[2]
                        thiscut = actions[3]
                        if debugPrint:
                            print('add_millstop_thiscoil result:', cutnow, coil_DefectList, cutlist)
                        #thiscut = cutlist[0].length
                        #thisdefectlength = cutlist[0].defect_length

                        reoptimize = True
                        if debugPrint:
                            pass
                            print('set reoptimize = True')
                            print('break')




                    # Mill stop affects next coil
                    #This should not happen with specified mill stops in data set
                    else:

                        if debugPrint:
                            pass
                            print('add millstop to next coil')
                        #exit()
                        #millstop_carry = 153.0 - running_Coil_Length
                        if debugPrint:
                            pass
                            print('millstop carry, running coil length', millstop_carry, running_Coil_Length)
                        newfault = 0

                    # We clear static mill stop so we don't do it again
                    static_millStop = -1000

                    if debugPrint:
                        print('first break', )
                        print('TCO pipe was ', tco_PipeLength, 'when mill stop occured')
                    break
                # No Mill stop continue
                else:
                    if cutnow:
                        print('cutnow')
                        break
                    pass

            # thiscut loop


            # TCO end of cycle reached - let's cut the pipe

            coil_pipe = '{0:0>4}'.format(str(coil_num)) + ' ' + '{0:0>2}'.format(str(pipe_number))
            cutpipe = (coil_pipe, thiscut, thisdefectlength)
            if debugPrint:
                ('cutpipe:',cutpipe)
            newpipes.append(cutpipe)

            coil_pipelength += thiscut
            # running_Coil_Length -= thiscut
            if debugPrint:
                pass
                print('cutnow,reopt,newfault',cutnow,reoptimize,newfault)
                print('Finish TCO Cut Pipe;', pipe_number, 'Length = ', tco_PipeLength, thiscut)
                print('defect list:', coil_DefectList)

                ### End While tco Pipelength < thiscut
            if debugPrint:
                print('add pipelength', thiscut, coil_pipelength, running_Coil_Length)


            if cutnow:
                # coil_DefectList = shift_defect(coil_Defectlist, thiscut - tco_PipeLength)
                print('cutnow')
                pass
                tco_PipeLength = 0
                pipe_number += 1
                break
            if reoptimize == True or newfault == 1:
                if debugPrint:
                    pass
                    print('reoptimize here')
                    print('cutlist = ',cutlist)
                    print('reopt,newfautl',reoptimize,newfault)

                tco_PipeLength = 0
                pipe_number += 1
                break
            tco_PipeLength = 0
            pipe_number += 1
            # end of for cut in cutlist
            if reoptimize:
                print('reoptimize2')
                break
            if debugPrint:
                print(coil_DefectList)

        # We have made the last cut up to the defect - so remove defect from list
        if running_Coil_Length > 0 and cutnow == False:
            if reoptimize == False:
                if debugPrint:
                    print('update coil - remove defect in coil:', coil_num)
                closest = get_ClosestDefect(coil_DefectList)
                thisdefect = coil_DefectList[closest]
                if debugPrint:
                    print(closest, 'current defect', thisdefect, thisdefect.location)
                if debugPrint:
                    print('CLOSEST:', closest,'Running coil length',running_Coil_Length)
                # if len(coil_DefectList) > 0 and millvar.hold_defect == False :
                #     if debugPrint:
                #         print('Im here')
                #     coil_Defectlist = remove_defect(coil_DefectList, closest)
                #     millvar.crushtest = True
                # else:
                #     if debugPrint:
                #         print('here')
                # reoptimize = False
                if int(running_Coil_Length) == closest:
                    pass
                else:
                    remove_defect(coil_DefectList,closest)
                if debugPrint:
                    print('remove closest defect',closest,running_Coil_Length)
                millvar.hold_defect = False
            else:
                if debugPrint:
                    pass
                    print('reoptimize is true')
            if debugPrint:
                pass
                print('call optimize')
            cutlist = optimize(coil_DefectList)

            newfault = 0
            if debugPrint:
                pass
                print('optimize  cutlist=',cutlist)
                print('Updated Coil: ', coil_DefectList)
            reoptimize = False

            if cutlist == []:
                break
            if debugPrint:
                print('new cutlist', cutlist)


        else:
            if running_Coil_Length > 0 and cutnow == True:
                cutnow = False
                if debugPrint:
                    print('we hit questionable reopt')
                    print(coil_DefectList, thiscut, tco_PipeLength)

                    # newcutlist = cutlist[1:]
                    # cutlist = newcutlist

        if debugPrint:
            print('end of coil defect list')
            print(coil_DefectList)

        running_Coil_Length = get_coil_length(coil_DefectList)

    ### End while running coil - finish and return
    if debugPrint:
        print(coil_pipelength, coil_length)

    # Current Coil has been run out. if we cut into next coil, headChop is removed from CAPL for next coil
    # headChop = running_Coil_Length
    headChop = round(coil_length - coil_pipelength, 1)
    if debugPrint:
        print('Headchop = ', headChop)
    #if headChop < .5:
        #headChop = 0
    if debugPrint:
        print('*** End of Coil *** headChop, running coil length', headChop, running_Coil_Length)
        print(running_Coil_Length)
    coil_output = [headChop, newpipes, coil_DefectList, millstop_carry]
    if debugPrint:
        print('normal return', coil_output)

    return coil_output


def run_coil_list(coil_List):
    pipelist = []
    coil_num = 0
    headChop = 0
    dLoc = 0
    dLen = 0
    dType = 0
    millstop_carry = 0
    if debugPrint:
        print('Start run_coil_list:', coil_List)
    print('Simulation coil count =', len(coil_List))
    for coil in coil_List:
        if coil_num == 0:
            # headChop = -millvar.crossweld_BadLength
            if debugPrint:
                print('first coil', coil, headChop)

        else:
            if debugPrint:
                print('coil', coil)
        # if we want to have crossweld from first coil
        coil_num += 1

        if debugPrint:
            print('*********\n*********\n New Coil:', coil_num, '\n*********\n*********\n', coil)

        coil_DefectList = load_Coil(coil, headChop)
        #
        # #coil_DefectList = add_defect(coil_DefectList, dLoc, dLen, dType)
        coil_DefectList = clean_Defects(coil_DefectList)
        if debugPrint:
            print('**new coil defect list', coil_DefectList)

            # --- Run a coil
        if debugPrint:
            print('Call run coil')
        result = run_coil(coil, coil_num, headChop, millstop_carry)

        if debugPrint:
            print('coil run. Result =', result)

        headChop = result[0]
        if debugPrint:
            print('headchop = ', headChop)
        coilpipes = result[1]

        # print('coilpipes',coilpipes)
        old_defect = result[2]
        # if debugPrint:
        #     print('old defect = ',old_defect)
        pipelist.append(coilpipes)
        millstop_carry = result[3]
        if debugPrint:
            print('*************mill stop carry ******', millstop_carry)

        for key in old_defect:
            defect = old_defect[key]
            dLoc = defect.location
            dLen = defect.length
            dType = defect.defect_type

        coil_DefectList = clean_Defects(coil_DefectList)

        if debugPrint:
            print('Add ', headChop, ' to next coil')
            # print('cd1', coil_DefectList)
        millvar.running_Coil_Length = 0

    if debugPrint:
        print('end run_coil_list')
        # break

    # end for coil in coil_List
    return pipelist


#
#
# Create histogram bins for pipes that were created
# this is only used to help evaluate optimization results
#
def bin_pipes(coilpipes):
    bins = []
    b99 = millvar.max_Length*.99
    b98 = millvar.max_Length * .98
    b97 = millvar.max_Length * .97
    b95 = millvar.max_Length * .95
    b90 = millvar.max_Length * .90
    bmin = millvar.mill_Min_Length


    for coil in coilpipes:
        bin_99 = 0
        bin_98 =0
        bin_97 =0
        bin_95 = 0
        bin_90 = 0
        bin_min = 0
        bin_scrap=0

        bin_99Avg = 0
        bin_98Avg =0
        bin_97Avg =0
        bin_95Avg = 0
        bin_90Avg = 0
        bin_minAvg = 0
        bin_scrapAvg=0

        bin_99Len = 0
        bin_98Len =0
        bin_97Len =0
        bin_95Len = 0
        bin_90Len = 0
        bin_minLen = 0
        bin_scrapLen=0

        length_prime=0
        length_scrap=0
        for pipes in coil:
            for pipe in pipes:
                if debugPrint:
                    print(pipe)
                pipelen = 0
                pipelen = pipe[1] - pipe[2]
                length_prime+=pipelen
                length_scrap += pipe[2]
                if debugPrint:
                    (pipe, pipelen)
                if pipelen >= b99:
                    bin_99 += 1
                    bin_99Len +=pipelen
                else:
                    if pipelen >= b98:
                        bin_98 += 1
                        bin_98Len += pipelen
                    else:
                        if pipelen >= b97:
                            b97 += 1
                            bin_97Len += pipelen
                        else:
                            if pipelen >= b95:
                                bin_95 += 1
                                bin_95Len += pipelen
                            else:
                                if pipelen >= b90:
                                    bin_90 += 1
                                    bin_90Len += pipelen
                                else:
                                    if pipelen >= bmin:
                                        bin_min += 1
                                        bin_minLen += pipelen
                                    else:
                                        bin_scrap += 1
                                        bin_scrapLen += pipelen

        if bin_99 != 0:
            bin_99Avg = round(bin_99Len/bin_99,1)
        else:
            bin_99Avg=0
        if bin_98 != 0:
            bin_98Avg =round(bin_98Len/bin_98,1)
        else:
            bin_98Avg = 0
        if bin_97 != 0:
            bin_97Avg = round(bin_97Len / bin_97,1)
        else:
            bin_97Avg = 0
        if bin_95 != 0:
            bin_95Avg = round(bin_95Len / bin_95,1)
        else:
            bin_95Avg = 0

        if bin_90 != 0:
            bin_90Avg = round(bin_90Len / bin_90,1)
        else:
            bin_90Avg = 0

        if bin_min != 0:
            bin_minAvg = round(bin_minLen / bin_min,1)
        else:
            bin_minAvg = 0

        # if bin_scrap != 0:
        #     bin_scrapAvg = bin_scrapLen / bin_scrap
        # else:
        #     bin_scrapAvg = 0

        print('Total pieces for 99,98,97,95,90,min,scrap')
        print(bin_99,
              bin_98,
              bin_97,
              bin_95,
              bin_90,
              bin_min,
              )
        print('Average Lengths for 99,98,97,95,90,min')
        print(bin_99Avg,
              bin_98Avg,
              bin_97Avg,
              bin_95Avg,
              bin_90Avg,
              bin_minAvg
              )

        bins.append(bin_99)
        bins.append(bin_98)
        bins.append(bin_97)
        bins.append(bin_95)
        bins.append(bin_90)
        bins.append(bin_min)


        print('\n\n')
        print (bins)
        return bins


def group_pipes(coilpipes):
    for coil in coilpipes:

        primelen =0
        pipelen = 0
        pipecount = 0
        avglen = 0
        totalpipelen = 0


        wholescrapcount = 0
        wholescraplen = 0
        scraplen = 0
        for pipes in coil:
            for pipe in pipes:
                # print (pipe)
                pipelen = pipe[1] - pipe[2]
                # if debugPrint:
                #     print('pipelen, pipe 1, pipe2',pipelen,pipe[1],pipe[2])
                # print(pipelen,pipecount)
                if pipelen > millvar.mill_Min_Length:
                    primelen += pipelen
                    scraplen += pipe[2]
                    pipecount+=1
                # print(totalpipelen)
                else:
                    scraplen += pipe[1]
                if debugPrint:
                    print('Added Pipe:',pipe,'primelen,scraplen',primelen,scraplen)

                totalpipelen+=pipe[1]


    avglen = primelen / pipecount

    print('Group Pipe - average pipe length: ,', round(avglen,1), ',scrap length: ,', round(scraplen, 1)
          ,'\nGroup Pipe - Prime pipe length:', round(primelen,1),'Total Pipe Length',round(totalpipelen,1))

    print('Group Pipe - Yield = ',round(primelen/totalpipelen,3))
    pass


def main():
    millvar.max_Length = 48.0  # 63.7
    millvar.crossweld_BadLength = 8.0
    millvar.alt_Maximum_Length = 79.9  # 48.0
    millvar.alt_Minimum_Length = 40.0
    millvar.millStop_BadLength = 20.0
    millvar.mill_Max_Length = 83.5
    millvar.mill_Min_Length = 30.0
    millvar.millStop_Frequency = 15
    millvar.tco_ClampEngageLength = 5
    millvar.tear_BadLength = 1
    millvar.total_CoilLength = 0.0
    millvar.total_PipeLength = 0.0
    millvar.nextbad = []
    millvar.simulation_step = .1
    # initialize pipe length
    millvar.tco_PipeLength = 0
    headChop = 0
    yieldlist = []
    coils_per_run = 1
    # set to indicate how many simulated runs for a given mill stop frequency
    runs_per_frequency = 10

    # set min and max frequency of mill stops per 10000 feet
    min_stop_frequency = 10
    max_stop_frequency = 20

    coilpipes = []

    millvar.running_Coil_Length = 0
    coil_DefectList = []
    # create sample coil lineup
    coil_List = create_simulation_coil_list(200)
    for coil in coil_List:
        print(coil)
        pass
    total_coilLength = 0
    starttime = time.strftime("%H:%M:%S")
    print('Begin simulation ', starttime, )
    if richOptimize:
        print('New Optimization Algorithm')
    else:
        print('Brock Optimization Algorithm')
    print('Parameters: millvar.millStop_BadLength: ',
          millvar.millStop_BadLength, '  millvar.crossweld_BadLength:  ', millvar.crossweld_BadLength, '\n')
    resultlist = []
    for millvar.max_Length in [80]:
        for millvar.alt_Minimum_Length in [30]:

            for millvar.mill_Min_Length in [30]:
                print('Begin Trial Run')

                coilpipes = []

                pipecount = 0
                pipelength = 0.0
                coillength = 0.0
                wholescraplength = 0.0
                wholescrapcount = 0
                scraplength = 0.0
                scrapcount = 0
                # for coil in coil_List:
                #     coillength += coil[0]

                runpipes = run_coil_list(coil_List)
                pipelength = 0
                coilpipes.append(runpipes)
                if printPipes:

                    for pipes in runpipes:
                        for pipe in pipes:
                            print(pipe[0], ',', pipe[1], ',', pipe[2])
                            pass
                print('Run Parameters: Max Length =  ', millvar.max_Length,'Min Length =',millvar.mill_Min_Length,
                      ' alt min length = ', millvar.alt_Minimum_Length, ' simulation_step= ', millvar.simulation_step)
                #print('Coil Length','Pipe Length','Pipe Count','Scrap Length','Yield')
                #result = (evaluate_pipes(runpipes, coil_List))

                #resultlist.append(result)
               # print('Yield =', result[4])
                #print(result)
                group_pipes(coilpipes)
                binlist = bin_pipes(coilpipes)

    total = 0
    # for result in resultlist:
    #     print(result)
    #     total += result[6]
    # print ('Average Yield = ',total/len(resultlist))




    ##  yieldlist.append(result[6]
    ##  print ('Average Yield ',avg_yield = sum(yieldlist)/ float(len(yieldlist)))

    total_coil_length = 0
    total_coil_defect_length = 0
    for coil in coil_List:


        total_coil_length += coil[0]
        total_coil_defect_length += 2*coil[4]
    print('coil totals:',total_coil_length,total_coil_defect_length)
    if debugPrint:
        print(coil_List)
    endtime = time.strftime("%H:%M:%S")
    print('End Simulation', endtime)




main()
