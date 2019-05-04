# LDAP-Data-Poster
Provides a means of posting changes from one LDAP server to another, these do not have to the same type of server.


 Across time different vendors and types of software that provide LDAP services become available for use or are retired.

 Many of the LDAP servers available provide the ability to multi-master replication of their data, but typically do not support replication to another type of LDAP server. For instance if you needed to move away from using the Sun Direcotry server, ODSEE (oracle directory server enterprise edition) , because the supplier of the software was ending support for it, you would require a way of moving the data from the old directory server to a new one, such as ds389. If you needed to have both the old and new servers running in parallel to allow for a seamless transition you would want to be able to have replication between the two directories that would keep their contents in sync . Such inter directory replication not included with many LDAP products.

I was able to use python to query two live directories and check the time of last update of the records and then use python to write the new record from the old directory to the new one. This method provides 1 way replication of changes between the the 2 systems.   
