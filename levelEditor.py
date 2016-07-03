import pygame
import sys

screen = pygame.display.set_mode((0, 0))
screen_size = screen.get_size()
_map = [(0, 0), (20, 0), (30, 0)]
scrollX = 0
scrollY = 0
selected = _map[-1]

scrolling = False
scrollStart = False
scrollSXStart = False
scrollSYStart = False

PPM = 20.0
clock = pygame.time.Clock()
while True:
	screen.fill((230, 230, 230))

	if scrolling:
		mp = pygame.mouse.get_pos()
		xDiff = mp[0] - scrollStart[0]
		yDiff = mp[1] - scrollStart[1]
		scrollX = xDiff + scrollSXStart
		scrollY = yDiff + scrollSYStart

#~
	for x in range(int(round(scrollX % PPM)), screen_size[0], int(round(PPM))):
		pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, screen_size[1]))
	for y in range(int(round(scrollY % PPM)), screen_size[1], int(round(PPM))):
		pygame.draw.line(screen, (20, 20, 20), (0, y), (screen_size[0], y))

	pygame.draw.circle(screen, (20, 20, 20), (int(round(PPM)), int(round(PPM))), int(round(PPM)))
	pygame.draw.circle(screen, (20, 20, 20), (int(round(PPM)) * 7, int(round(PPM))), int(round(PPM)))

	for n, i in enumerate(_map):
		i = (int(round(i[0] * PPM)) + scrollX, int(round(i[1] * PPM)) + scrollY)
		pygame.draw.circle(screen, (20, 20, 20), i, 7)

		ni = i
		if n > 0:
			i = _map[n - 1]
			i = (int(round(i[0] * PPM)) + scrollX, int(round(i[1] * PPM)) + scrollY)
			pygame.draw.line(screen, (20, 20, 20), ni, i, 3)

	if selected:
		c = (20, 20, 20)
		lp = selected
		mp = pygame.mouse.get_pos()
		mx = (mp[0]) / PPM
		my = (mp[1]) / PPM
		mx = int(round(mx))
		my = int(round(my))
		mx *= PPM
		my *= PPM
		if mx <= _map[-1][0]:
			c = (200, 20, 20)
		mp = (mx, my)
		lp = (lp[0] * PPM + scrollX, lp[1] * PPM + scrollY)
		pygame.draw.line(screen, c, lp, mp, 3)

	pygame.display.flip()
	clock.tick(30)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 2:
				scrolling = True
				scrollStart = event.pos
				scrollSXStart = scrollX
				scrollSYStart = scrollY
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				x = (event.pos[0] - scrollX) / PPM
				y = (event.pos[1] - scrollY) / PPM
				x = int(round(x))
				y = int(round(y))
				if not selected:
					if (x, y) == _map[-1]:
						selected = (x, y)
				else:
					if (x, y) not in _map:
						if x > _map[-1][0]:
							selected = (x, y)
							_map.append((x, y))
			#		else:
			#			selected = False
			elif event.button == 2:
				scrolling = False
				scrollStart = False
			#elif event.button == 3:
			#	selected = False
			elif event.button == 4:
				PPM += 2.5
				print PPM
			elif event.button == 5:
				PPM -= 2.5
				if PPM <= 0:
					PPM = 1
