from card_matcher.webcam import Webcam
from card_matcher.card_detector import CardDetector
from card_matcher.card_finder import CardFinder

webcam = Webcam()
card_detector = CardDetector(webcam)
card_finder = CardFinder()
