import neat
import pickle
import sys
from snakeRunner import snakeRunner


# Driver for NEAT solution to FlapPyBird
def evolutionary_driver(n=0,load = False, save = False):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config')

    # Create the population, which is the top-level object for a NEAT run.
    if load:
        p = pickle.load(open("snakePopulation.pkl",'rb'))
        p.add_reporter(neat.StdOutReporter(False))
    else:
        p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.

    if save:
        s = 1
    else:
        s = 0
    if load:
        l = 1
    else:
        l = 0

    genFile = open("gen.txt","r")
    genFile.readline()
    genFile.readline()
    gen = genFile.readline()
    print(gen)
    genFile.close()

    genFile = open("gen.txt","w")
    genFile.truncate()
    genFile.write(str(s) + "\n" + str(l) + "\n" + str(gen))
    genFile.close()


    # Run until we achive n.
    if n == 0:
        n = None
        print(str(n))

    winner = p.run(eval_genomes, n=n)

    # dump
    pickle.dump(winner, open('winner.pkl', 'wb'))

    if save:
        pickle.dump(p, open('snakePopulation.pkl','wb'))


def eval_genomes(genomes, config):
    genFile = open("gen.txt","r")
    s = int(genFile.readline())
    l = int(genFile.readline())
    print("s: " + str(s))
    print("l: " + str(l))

    if l > 0:
        gen = int(genFile.readline())
        print(gen)
    else:
        gen = 0
        l = 1
    genFile.close()

    # Play game and get results
    idx,genomes = zip(*genomes)

    runner = snakeRunner(genomes, config,gen)
    #runner.configure(False,True)
    runner.run(True)
    results = runner.results

    top_score = 0
    for result, genomes in results:
        score = result["score"]
        steps = result["steps"]
        turns = result["turns"]
        idledToDeath = result["idledToDeath"]
        """scoreMultiplier = 200
        stepsMultiplier = 1
        turnsMultiplier = 5
        if score > 2:
            scoreMultiplier = 50
        if idledToDeath:
            stepsMultiplier = .1
            turnsMultiplier = .1
        fitness = (score * scoreMultiplier) + steps * stepsMultiplier + turns * turnsMultiplier"""
        fitness = steps + ((2**score) + (score**2.1)*500) - ((score**1.2) * ((.25*steps)**1.3))
        genomes.fitness = fitness

        if score > top_score:
            top_score = score

    print("The top score for this generation is: " + str(top_score))

    gen+=1
    genFile = open("gen.txt","w")
    genFile.write(str(s) + "\n" + str(l) + "\n" + str(gen))
    genFile.close()



def main():
    if len(sys.argv)>1:
        load = False
        save = False
        for arg in sys.argv:
            if arg == "-load":
                load = True
            if arg == "-save":
                save = True
        evolutionary_driver(int(sys.argv[1]),load, save)
    else:
        evolutionary_driver()

if __name__ == "__main__":
	main()
