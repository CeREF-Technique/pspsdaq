from export import Export

stuff = Export("titi", header=["yeah","great","such","header"])

stuff.writerow(["bla","tutu","truc"])
stuff.writerow(["bla2","tutu2","truc2"])

anotherStuff = Export("titi2", type="bla")
anotherStuff.writerow([1,2,3])
