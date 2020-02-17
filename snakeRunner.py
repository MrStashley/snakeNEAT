from snake import snakeGame
import neat
import time
import random
import pickle
import threading

def testDriver():
    snakeGameConfig = {
          "useKeys":False
    }

    game = snakeGame(snakeGameConfig);

    while not game.gameOver:
        input = game.simulPlay();
        if game.gameOver:
            break
        print(input)
        game.move(round(3 * random.random()))
        print(game.gameOver)

    print("Score " + str(game.score))

class snakeNN(object):
    def __init__(self,genome, config,name):
        self.genome = genome
        self.neural_network = neat.nn.FeedForwardNetwork.create(genome, config)
        self.name = name

    def test(self,input):
        output = self.neural_network.activate(input)
        return output.index(max(output))


class snakeRunner(object):

    def __init__(self, genomes = [], config = None, gen = 0):
        self.names = []
        nameFile = open("names.txt", "r")
        for line in nameFile:
            self.names.append(line)

        acheivementsFile = open("acheivements.txt","r")
        self.highestSteps = int(acheivementsFile.readline())
        random.seed(time.time())
        self.snakes = [snakeNN(genome,config,random.choice(self.names)) for genome in genomes] #initializes all the snakes in generation
        self.results = []
        self.game = snakeGame({
            "useKeys":False
        })
        self.highScore = 0
        self.highSteps = 0
        self.display = True
        self.displayTop = False
        self.gen = gen
        self.threads = []

    def addSnakesToRun(self,snakes):
        self.snakes.extend(snakes)

    def configure(self,display, displayTop):
        self.display = display
        self.displayTop = displayTop

    def run(self,save):
        for snake in self.snakes:
            self.test(snake)
            """if self.display:
                self.test(snake)                #tests all snakes and gets results
            else:
                t = threading.Thread(target=self.test, args=(snake,))
                t.start()
                self.threads.append(t)

        if not self.display:
            for t in self.threads:
                print(t)
                t.join()
        print("made it here")   """

        if self.displayTop:
            tempDisplay = self.display
            self.display = True
            self.test(self.highScoreSnake)
            self.display = tempDisplay

        if save and self.gen % 10 == 0:
            pickle.dump(self.highScoreSnake, open('highScoreGen' + str(self.gen)+ '.pkl', 'wb'))


    def test(self,snake):
        idleStepsCap = 1000
        game = self.game
        steps = 0
        idleSteps = 0
        while not game.gameOver: #simulates snake game with each snakeNN in generation
            score = game.score
            if self.display:
                input = game.simulPlay({
                    "gen":self.gen,
                    "name":snake.name,
                    "steps":steps,
                    "highScore":self.highScore
                });
            else:
                input = game.simulate();
            if game.gameOver or idleSteps > idleStepsCap:
                idledToDeath = False
                if idleSteps > idleStepsCap:
                    idledToDeath = True
                break
            output = snake.test(input) #gets output from snakeNN with input from game
            game.move(output)
            steps+=1 #increases amount of moves taken, needed to calculate fitness later
            if score == game.score:
                idleSteps+=1
            else:
                idleSteps = 0

        score = game.score #gets final game score
        turns = game.getTurns() #gets amount of turns in run
        if score > self.highScore:
            self.highScore = score
            self.highScoreSnake = snake #finds snakeNN object with the highest score for display purposes
        elif self.highScore == 0 and steps > self.highSteps:
            self.highSteps = steps
            self.highScoreSnake = snake
        elif steps > self.highSteps:
            self.highSteps = steps

        if score > 10 and steps > self.highestSteps:
            self.highestSteps = steps
            acheivementsFile = open("acheivements.txt","w")
            acheivementsFile.write(str(self.highestSteps))
            snake.name = "Urazek"
            pickle.dump(snake, open('Urazek.pkl', 'wb'))

        game.reset();
        self.results.append(({
            'score':score,
            'steps':steps,
            'turns':turns,
            'idledToDeath':idledToDeath,
            'network':snake.neural_network,
            'genome':snake.genome
        },snake.genome))
