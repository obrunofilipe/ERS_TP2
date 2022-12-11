import sys, socket

from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class Servidor:	

	clientInfo = {}
	rounds = 0
	total_frames = 0

	def __init__(self, video, dif_node):
		self.filename = video
		self.diffusion_node = dif_node

	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05)
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet():
				break
				
			data = self.clientInfo['videoStream'].nextFrame()
			if data:
				#frameNumber = self.clientInfo['videoStream'].frameNbr() + self.total_frames*self.rounds
				self.total_frames += 1
				try:
					address = self.clientInfo['rtpAddr']
					port = int(self.clientInfo['rtpPort'])
					packet =  self.makeRtp(data, self.total_frames) #frameNumber + self.total_frames*self.rounds)
					self.clientInfo['rtpSocket'].sendto(packet,(address,port))
				except:
					print("Connection Error")
					print('-'*60)
					traceback.print_exc(file=sys.stdout)
					print('-'*60)
			else:
				self.clientInfo['videoStream'] = VideoStream(self.filename)
				#self.rounds += 1
		# Close the RTP socket
		self.clientInfo['rtpSocket'].close()
		print("All done!")

	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0
		
		rtpPacket = RtpPacket()
		
		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		print("Encoding RTP Packet: " + str(seqnum))
		
		return rtpPacket.getPacket()

	
	def main(self):
		try:
			# Get the media file name
			#self.filename = video
			print("Using provided video file ->  " + self.filename)
		except:
			print("[Usage: Servidor.py <videofile>]\n")
			self.filename = "movie.Mjpeg"
			print("Using default video file ->  " + self.filename)

		# videoStram
		self.clientInfo['videoStream'] = VideoStream(self.filename)
		# socket
		self.clientInfo['rtpPort'] = 6000
		self.clientInfo['rtpAddr'] = socket.gethostbyname(self.diffusion_node)
		print("Sending to Addr:" + self.clientInfo['rtpAddr'] + ":" + str(self.clientInfo['rtpPort']))
		# Create a new socket for RTP/UDP
		self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.clientInfo['event'] = threading.Event()
		self.clientInfo['worker']= threading.Thread(target=self.sendRtp)
		self.clientInfo['worker'].start()





