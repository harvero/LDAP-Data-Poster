
#!/usr/bin/env python
#
## program  : LDAP_data_poster post_change.py
##
## function : copies LDAP objects from 1 DS to another
##               you: hey that is 1 way replication
##               me:  you are correct  :)
##     version           :  1.0
##     by                :  Bob Harvey
##
##     updates:
##
##    Replace "myco" in the DNs with your base DN.
##    You will also need to replace the ldap servers names and ports
##      as well as the bind account and password.
#####

import sys
import syslog
import pyping
import re
import os
import os.path
import datetime
import cStringIO
import glob
import errno
import ldap
import ldap.modlist as modlist
import socket

def mylogger ( inputtxt ):
  if os.isatty(sys.stdin.fileno()):
    print inputtxt
  else:
    syslog.syslog(inputtxt)

def check_server(address, port):
  # Create a TCP socket
  s = socket.socket()
  s.settimeout(10)
  #print "Attempting to connect to %s on TCP port %s" % (address, port)
  try:
        s.connect((address, port))
        #print "    PASS: Connected to %s on port %s" % (address, port)
        return True
  except socket.error, e:
        #print "                              FAILED: Connection to %s on port %s failed: %s" % (address, port, e)
        return False

def normaldn ( inputdn ):
  # correct deltas in the DN syntax
  dn = inputdn
  if re.match(r'.*\sdc=com', dn )  :
    oulen = len (dn)
    keepsize = oulen - 7
    cutsize = oulen -6
    new1 = dn[:keepsize]
    new2 =  dn[cutsize:]
    newdn = new1 + new2
    #print  "dn : " + dn    +   "   new dn :" + newdn
    dn = newdn
  if re.match(r'.*\sou=profile,dc=myco,dc=com', dn )  :
    # e.g. cn=orpo, ou=profile,dc=myco,dc=com 
    oulen = len (dn)
    keepsize = oulen - 28
    cutsize = oulen - 27
    new1 = dn[:keepsize]
    new2 =  dn[cutsize:]
    newdn = new1 + new2
    #print  "dn : " + dn    +   "   new dn :" + newdn
    dn = newdn
  if re.match(r'.*ou=people,dc=myco,\sdc=com', dn )  :
    oulen = len (dn)
    keepsize = oulen - 7
    cutsize = oulen -6
    new1 = dn[:keepsize]
    new2 =  dn[cutsize:]
    newdn = new1 + new2
    dn = newdn
  if re.match(r'.*\sou=group,dc=myco,dc=com', dn )  :
    oulen = len (dn)
    keepsize = oulen - 26
    new1 = dn[:keepsize]
    new2 =  'ou=group,dc=myco,dc=com'
    newdn = new1 + new2
    #print  "dn : " + dn    +   "   new dn :" + newdn
    dn = newdn
  if re.match(r'.*\sou=netgroup,dc=myco,dc=com', dn )  :
    oulen = len (dn)
    keepsize = oulen - 29
    new1 = dn[:keepsize]
    new2 =  'ou=netgroup,dc=myco,dc=com'
    newdn = new1 + new2
    #print  "dn : " + dn    +   "   new dn :" + newdn
    dn = newdn
  if re.match(r'.*ou=Netgroup,dc=myco,dc=com', dn )  :
    oulen = len (dn)
    keepsize = oulen - 28
    new1 = dn[:keepsize]
    new2 =  'ou=netgroup,dc=myco,dc=com'
    newdn = new1 + new2
    #print  "dn : " + dn    +   "   new dn :" + newdn
    dn = newdn
  if re.match(r'.*ou=Aliases,dc=myco,dc=com', dn )  :
    oulen = len (dn)
    keepsize = oulen - 27
    new1 = dn[:keepsize]
    new2 =  'ou=aliases,dc=myco,dc=com'
    newdn = new1 + new2
    #print  "dn : " + dn    +   "   new dn :" + newdn
    dn = newdn
  if re.match(r'.*\sou=aliases,dc=myco,dc=com', dn )  :
    oulen = len (dn)
    keepsize = oulen - 28
    new1 = dn[:keepsize]
    new2 =  'ou=aliases,dc=myco,dc=com'
    newdn = new1 + new2
    #print  "dn : " + dn    +   "   new dn :" + newdn
    dn = newdn
  return dn

def repit():

  mylogger ("run start")

  odseelist = [ "ldap17" ,  "ldap18" ]
  frlist =  [ "ldap27" , "ldap28"  ]
  odseesrv = ""
  frsrvr = ""

  frport = 1389
  odseeport = 389


  mylogger ("seeking an odsee")
  for srv in odseelist:
    rc = check_server( srv , 389 )
    #rc = pyping.ping(srv)
    #if rc.ret_code == 0:
    if rc == True:
      mylogger ("selected: " + srv  ) 
      odseesrv = srv
      break
    else:
      mylogger ("bad ping of " + srv )

  mylogger ("seeking a fr server")
  for srv in frlist:
    #rc = pyping.ping(srv)
    rc = check_server( srv , 1389 )
    #if rc.ret_code == 0:
    if rc == True:
      mylogger ("selected:  " + srv)
      frsrv = srv
      break
    else:
      mylogger ("bad ping of " + srv)

  odconnect = "ldap://" + odseesrv + ":" + str (odseeport) + "/"
  frconnect = "ldap://" + frsrv + ":" + str(frport) + "/"


  mylogger ( "checking for the listener for  ODSEE Source : " + odconnect )

  rc = check_server (odseesrv  , odseeport )

  if rc == False:
    mylogger ("Unable to connect to " + odconnect )
    mylogger ("ending run")
    return   

  mylogger ( "checking the listener for ForgeRock Target : " + frconnect ) 

  rc = check_server (frsrv  , frport )
  if rc == False:
    mylogger ("Unable to connect to " + frconnect )
    mylogger ("ending run")
    return

  # Open a connection ODSEE
  try:
    l = ldap.initialize(odconnect)
  except ldap.LDAPError, e:
    mylogger ( e )

  l.simple_bind_s("cn=directory manager",PW)

  #return 
  #exit()

  # open another connection FR
  try:
    lfr = ldap.initialize(frconnect)
  except ldap.LDAPError, e:
    mylogger ( e )

  lfr.simple_bind_s("cn=directory manager",PW2)
  
  #baseDN = "ou=aliases,dc=myco,dc=com"
  baseDN = "ou=People,dc=myco,dc=com"
  searchScope = ldap.SCOPE_SUBTREE
  searchScopeBase = ldap.SCOPE_BASE
  ## retrieve all attributes - again adjust to your needs - see documentation for more options
  #retrieveAttributes = None 
  #retrieveAttributes = [ '*', 'userPassword', 'isMemberOf', 'nsAccountLock' ] 
  #retrieveAttributes = [ '*', 'userPassword', 'nsAccountLock', 'modifyTimestamp'  ] 
  #retrieveAttributes = [ '*', 'userPassword', 'nsAccountLock', 'createTimestamp' , 'modifyTimestamp' , 'passwordPolicySubentry'  ] 
  
  retrieveAttributes = [ '*', 'userPassword', 'nsAccountLock', 'createTimestamp' , 'modifyTimestamp'  ] 
  
  searchFilter = "objectClass=*"
  #searchFilter = "uid=bo*"
  #oulist = [  "ou=people,dc=myco,dc=com" ]
  # below is the good list
  

  oulist = [  "ou=people,dc=myco,dc=com" ,  "ou=group,dc=myco,dc=com" , "ou=netgroup,dc=myco,dc=com" , 'ou=aliases,dc=myco,dc=com'  , 'automountMapName=auto_home,ou=maps,dc=myco,dc=com'  ]
  
  
  for myou in oulist:
    mylogger ( "working on " + myou )
    try:
	#ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
	ldap_result_id = l.search(myou, searchScope, searchFilter, retrieveAttributes)
	result_set1 = []
	while 1:
		result_type, result_data = l.result(ldap_result_id, 0)
		if (result_data == []):
			break
		else:
			## here you don't have to append to a list
			## you could do whatever you want with the individual entry
			## The appending to list is just for illustration. 
			if result_type == ldap.RES_SEARCH_ENTRY:
				result_set1.append(result_data)

        ldap_result_id = l.search(myou, searchScopeBase, searchFilter, retrieveAttributes)
        result_set2 = []
        while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                if (result_data  == []):
                        break
                else:
                        ## here you don't have to append to a list
                        ## you could do whatever you want with the individual entry
                        ## The appending to list is just for illustration.
                        if result_type == ldap.RES_SEARCH_ENTRY:
                                result_set2.append(result_data)

        result_set = ( result_set2 + result_set1 )
	#print result_set

### get what exists
  # enable this try under the try above - we need to check if the parent exists in the target
        try:
          ldap_result_id = lfr.search(myou, searchScope, searchFilter, retrieveAttributes)
          onfile_set1 = []
          while 1:
                result_type, result_data = lfr.result(ldap_result_id, 0)
                if (result_data == []):
                        break
                else:
                        ## here you don't have to append to a list
                        ## you could do whatever you want with the individual entry
                        ## The appending to list is just for illustration.
                        if result_type == ldap.RES_SEARCH_ENTRY:
                                onfile_set1.append(result_data)

          ldap_result_id = lfr.search(myou, searchScopeBase, searchFilter, retrieveAttributes)
          onfile_set2 = []
          while 1:
                result_type, result_data = lfr.result(ldap_result_id, 0)
                if (result_data  == []):
                        break
                else:
                        if result_type == ldap.RES_SEARCH_ENTRY:
                                onfile_set2.append(result_data)
                               
          onfile_set = ( onfile_set2 + onfile_set1 )
          onfile = {}
          for myonfile in onfile_set:
            for onfiledn , onfileentry in myonfile:
              try:
                value = onfileentry['modifyTimestamp'][0]
              except:
                value = onfileentry['createTimestamp'][0]
              lastupdate  = value
              myelement = { onfiledn : value }
              onfile.update(myelement)
              #print myelement  # use this to see the targets
              #print onfile
          #print onfile
          #exit()    
          #for d1  in onfile:
          #  print onfile[d1] 

          #exit()
###### add the except block here
        except ldap.LDAPError, e:
                myobj = e.args[0]
                mydesc =  myobj['desc']
                mystr = str (mydesc )
                mylogger ( mystr + " " + dn )
                mylogger (  e )

#####
        
	#print result_set
        #for dn,entry in result_set:
        
        sourcednlist = [];

        mylogger ( "    " + "checking Source values against Target" )
        for myr in result_set:   # result_set are the source values from odsee
          #print myr # this is tuple made of string and dicts that contain lists

          for dn, entry in myr:   
            noupdate = 0
            noadd = 0
            if re.search( 'cn=cat,ou=group,dc=myco,dc=com', dn )  :
              continue
          
            dn =  normaldn( dn )
            sourcednlist.append( dn ); 
             
            #print  "fetched DN: " + dn
            #continue

            #try:     # we do not need to deal with this since the fr policy have a filter
            #   sourcepolicy = entry['passwordPolicySubentry'][0]
            #except:
            #  sourcepolicy = 'not found'
            #try:
            #  sourcelock = entry['nsAccountLock'][0]
            #except:
            #  sourcelock = 'not set'
            #print "Source Policy " + sourcepolicy
            #print "Source Lock " + sourcelock
             # if sourcepwlock == "true" then we have stuff to do
              #
            #userpolicy = 'cn=DirectorypwdPolicyUser,cn=pwpolicy,cn=etc,dc=myco,dc=com'
            #if sourcepolicy == userpolicy :
            #   sourcepolicy = "cn=Track Last Login Time,cn=Password Policies,cn=config"
            #   del entry['passwordPolicySubentry']
            #   entry['ds-pwp-password-policy-dn'] =   sourcepolicy  
              
            if dn not in onfile:   # we need to add a new recors
              mylogger ( "     " +  dn + ": not on file in the result set from the target" )
              noadd = 1
            else:
              #print dn + ": was found on file"  # uncomment to debug
              try:
                value = entry['modifyTimestamp'][0]
              except:
                value = entry['createTimestamp'][0]
              lastupdate  = value
              onfilelastupdate = onfile[dn]
              onfileLUD = onfilelastupdate[:14]
              LUD = lastupdate[:14]
              #print lastupdate + " " + LUD + " " + onfilelastupdate  + " " + onfileLUD
              if LUD >  onfileLUD:
                #print lastupdate + " " + LUD + " " + onfilelastupdate  + " " + onfileLUD
                mylogger ( "Target: " + onfileLUD + " Source: " + LUD +  " Target is older and requires an update : " + dn )
                noupdate = 1
              ##continue
              #try:
              #  sourcepwpolicy = entry['passwordPolicySubentry'][0] 
              #except: 
              #  sourcepwpolicy = 'not found'
              #print sourcepwpolicy
              #try:
              #  sourcelock = entry['nsAccountLock'][0]
              #except:
              #  sourcepwlock = 'not set'
              #print "Source Policy " + sourcepwpolicy
              #print "Source Lock " + sourcepwlock
              ## if sourcepwlock = "true" then we have stuff to do
              ## 


            if noupdate == 0 and noadd == 0 :
              continue
            #myuid = ''.join(  entry['uid'] )
            process = 1 
            #for key in entry:
            for key in list(entry):
              value = entry[key][0]
              #if re.search( 'cn=user-dmed-dev-global', dn )  :
              #   print "The key: " + key + " The value: " + value
              #   print key + " ".join(entry[key])

              if value == "":
                 entry[key][0] = "no value provided"
              #print key + " : " + value
              if key == "nsAccountLock" and value == "true":
                 del entry[key]
                 entry["ds-pwp-account-disabled"] = "true"
        #        print "Skipping locked account"
                 #process = 0
             #   try: 
             #     lfr.delete_s(newdn) 
             #     print "Deleted inactive copy"
             #   except:
             #     break
             #   break
              if key == "nsAccountLock" and value != "true":
                del entry[key]
              if key == "modifyTimestamp":
                del entry[key]
              if key == "createTimestamp":
                del entry[key]
              if key == 'mailHost' and value == "":
                entry['mailHost'] = 'mailHost' 
              #if key == 'objectClass' and value.lower() == "nisNetgroup".lower() and re.search( 'cn=user-', dn )  :
              if key == 'objectClass' and  re.search( 'cn=user-', dn ) and "nisNetgroup" in str(entry[key])  :
                #if "account" in entry[key]:
                if "account" in str(entry[key]):
                  #print "account found in netgroup" 
                  a = 1 # filler
                else:
                  #print "account Not found in netgroup "  + dn + " adding an account object class"
                  entry[key].append ( "account" ) ### this does not work!!!!!
                
              if key == 'aci' and  re.search( 'cn=hosts,cn=etc', dn )  :
                del entry[key]
              if key == 'status' and  re.search( 'cn=masters,cn=etc,dc=myco,dc=com', dn )  :
                del entry[key]


            if noadd == 1: 
              #  continue
              #print dn + ": in the add block"
              mylist = list (myr)
              a = 0
              #print 'CN: ' + mycn
              #print 'loginShell: '.join( entry['loginShell'] )
              #myuid = ''.join(  entry['uid'] )
              #print 'uid: ' + myuid
              #newdn = "uid=" + myuid + ",ou=mypeople,dc=myco,dc=com"             
              #print 'New DN: ' + newdn

              #mylist[0] = newdn
              newdn = dn 
              ldif = modlist.addModlist(entry)
              try: 
                lfr.add_s( newdn, ldif  )
                mylogger ( "            Added: " + newdn  )
                
              except ldap.LDAPError, e:
                #print e
                #print e.args[0]
                myobj = e.args[0]
                mydesc =  myobj['desc']
                #print mydesc
                mystr = str (mydesc )
                # {'desc': 'Already exists'}
                if  mystr == 'Already exists':
                  mylogger ( "                     record exists already" )
                  continue 
                else:
                 mylogger ( mystr + " " +  e + " " +  newdn)
              #else:
              #    print "Added: " + newdn 
            #else: # noadd != 1 here for an update 
            if noupdate == 1 :
              ldif = modlist.addModlist(entry)
              try:
                lfr.delete_s(dn) 
              except ldap.LDAPError, e:
                myobj = e.args[0]
                mydesc =  myobj['desc']
                mystr = str (mydesc )
                mylogger ( mystr + " " + dn + " is not adding at line 518 " ) 
                #mylogger ( mystr + " " +  e + " " + dn ) 
              try:
                lfr.add_s( dn, ldif  )
                #lfr.modify_s( dn, ldif  )
              except ldap.LDAPError, e:
                myobj = e.args[0]
                mydesc =  myobj['desc']
                mystr = str (mydesc )
                mylogger ( mystr + " " + e + " " + dn )
              else:
                mylogger ( "Updated: " + dn )
 
            
            #print 
            #print 
            #print 
            #exit ();
          #exit()
        
        mylogger ( "    checking Target values against Source")
        for myon in onfile_set:  # look through the target set
          for ondn , entry in myon:
             #print ondn
             if re.match(r'.*cn=masters,cn=etc,dc=myco,dc=com', ondn )  :
               continue
             if ondn not in sourcednlist:
                mylogger ( "       "  + ondn + " is not in source and it needs to be removed from the target")
                try:
                  lfr.delete_s(ondn)
                  mylogger ( "Deleted inactive copy" )
                except:
                  break
                break


    except ldap.LDAPError, e:
	mylogger (e)
  mylogger ("end run")
#end  repit

def main ():
  repit()

if __name__ == "__main__":
    ret = main()


							


