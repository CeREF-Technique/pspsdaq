from export import Export

stuff = Export("titi", header=["yeah","great","such","header"])

stuff.writerow(["bla","tutu","truc"])
stuff.writerow(["bla2","tutu2","truc2"])

another2Stuff = Export("toto", type="xlsx",header=["t","u","w"])
another2Stuff.writerow([1,2,3])
another2Stuff.writerow([4,5,6])
another2Stuff.writerow([7,8,9])

another3Stuff = Export("toto2", type="xml",header=["t","u","w"])
another3Stuff.writerow([1,2,3])

anotherStuff = Export("titi2", type="bla")
anotherStuff.writerow([1,2,3])
