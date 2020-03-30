class Body(object):
	"""
    Creates an object that height and weight of a person.
    """

	def __init__(self, weight, height):
		self.measure = {'weight':weight, 'height':height}
             
	def height(self):
		
		h = self.measure['height']
		return float(h)
		
	def weight(self):
		
		w = self.measure['weight']
		return float(w)

	def addWeight(self, x):

		we = self.measure['weight']
		newW = float(float(we)+float(x))
		self.measure['weight'] = newW
		return newW        
      
	def convertHeight(self):
		"""
		Converts the height from inches to centimeters

		"""
		heightp = self.height()*2.54
		return(heightp)

	def convertWeight(self):
		"""
		Converts the weight from pounds to kilograms
		"""
		weightp = self.weight()*0.4536
		return(weightp)


