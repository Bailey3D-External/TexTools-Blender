# Returns a looped value between min - max
def clamp_loop(current, min, max):

	if min == max:
		return min

	if current < min:
		return max

	if current > max:
		return min

	return current

# Returns a looped index within a list
def clamp_loop_list(index, list):
	return clamp_loop(index, 0, len(list)-1)
