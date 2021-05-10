# Untitled - By: herve - ven. déc. 27 2019
#https://www.makeblock.com/project/me-encoder-motor-driver
#http://docs.micropython.org/en/latest/library/pyb.html

from pyb import I2C, delay
import ustruct


class motor :

    CMD_MOVE_SPD = 0x05
    HEADER = [0xA5, 0x01]
    END = 0x5A



    def __init__(self,pin, addr, slot) :
        ''' Constructeur de moteur meEncoder
        pin : patte du bus I2C (2 ou 4)
        addr : adresse de l'esclave
        slot : slot du moteur (1 ou 2)
        '''
        self.__slot = slot - 1
        self.__addr = addr
        self.__i2c = I2C(pin)

    def close(self) :
        '''ferme la communication I2C'''
        self.__i2c.deinit()

    def __sendData(self,data):
        '''Envoi les donnees sur I2C
        arg[in] -> data :  donnees a envoyer
        '''
        self.__i2c.init(I2C.MASTER)
        self.__i2c.send(data,self.__addr)

    def __sendAndReceive(self,data,lengthOfReception) :
        '''Envoi les donnees sur I2C et recoit une reponse
        arg[in] -> data :  donnees a envoyer
                -> lengthOfreception : longueur du message a recevoir (octets)
        arg[out] _> message recu
        '''
        self.__sendData(data)
        return self.__i2c.recv(lengthOfReception,self.__addr)

    def scan(self) :
        ''' Scan les esclaves connecte
        arg[out] -> liste des adresses
        '''
        self.__i2c.init(I2C.MASTER)
        listOfSlaves = self.__i2c.scan()
        return listOfSlaves

    def runSpeed(self,speed) :
         ''' Commande la rotation du moteur a une vitesse
         arg[in] -> speed : vitesse de rotation [-200,+200]
         '''
         self.__i2c.init(I2C.MASTER)
         data = bytearray([self.char2byte(self.__slot),motor.CMD_MOVE_SPD]+self.float2bytes(speed))
         lrc = self.lrcCalc(data)
         print (data)
         trame=bytearray(self.HEADER+self.long2bytes(6))+data+bytearray([lrc,self.END])
         self.__sendData(trame)



    def lrcCalc(self,data) :
        '''Calcul le CRC
        '''
        lrc = 0x00
        for byte in data :
            lrc ^= byte
        return lrc

    def float2bytes(self,fval):
         val = ustruct.pack("f",fval)
         #return [ord(val[0]),ord(val[1]),ord(val[2]),ord(val[3])]
         return [val[0],val[1],val[2],val[3]]

    def long2bytes(self,lval):
         val = ustruct.pack("l",lval)
         #return [ord(val[0]),ord(val[1]),ord(val[2]),ord(val[3])]
         return [val[0],val[1],val[2],val[3]]

    def short2bytes(self,sval):
         val = ustruct.pack("h",sval)
         #return [ord(val[0]),ord(val[1])]
         return [val[0],val[1]]
    def char2byte(self,cval):
         val = ustruct.pack("b",cval)
         #return ord(val[0])
         return val[0]


class Bob:

    def __init__(self):
        self.motor1 = motor(4,9,1)
        self.motor2 = motor(4,9,2)

    def runTwoMotors(self, speed1, speed2):
        self.motor1.runSpeed(speed1)
        delay(100)
        self.motor2.runSpeed(-speed2)

    def turnLeft(self, speed, himself=True):
        if himself:
            self.runTwoMotors(0, -speed)
        else:
            self.motor2.runSpeed(-speed)

    def turnRight(self, speed, himself=True):
        if himself:
            self.runTwoMotors(speed, 0)
        else:
            self.motor1.runSpeed(speed)


bob = Bob()
bob.runTwoMotors(200, 200)
delay(5*10**3) # 5s
bob.turnLeft(200, himself=False)
delay(5*10**3) # 5s
bob.turnRight(200, himself=False)
