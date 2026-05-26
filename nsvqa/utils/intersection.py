def group_with_gaps(nums, max_gaps=2):
    if not nums:
        return []
    groups = []
    current_group = [nums[0]]
    gaps = 0

    for i in range(1, len(nums)):
        if nums[i] - nums[i-1] == 1:
            current_group.append(nums[i])
        elif nums[i] - nums[i-1] <= max_gaps + 1:
            # fill in the gap logically
            current_group.extend(range(nums[i-1]+1, nums[i]+1))
            gaps += nums[i] - nums[i-1] - 1
            if gaps > max_gaps:
                groups.append(current_group[:- (nums[i] - nums[i-1] - 1)])
                current_group = [nums[i]]
                gaps = 0
        else:
            groups.append(current_group)
            current_group = [nums[i]]
            gaps = 0

    groups.append(current_group)
    return groups

def intersection_with_gaps(indices, max_gaps=8): # smart set intersection
    if not indices:
        return []
    if any(len(d) == 0 for d in indices):
        return []

    non_empty = [s for s in indices if s]
    if not non_empty:
        return []
    if len(non_empty) == 1:
        return list(non_empty[0])

    A = set(indices[0])
    B = set(indices[1])
    combined = sorted(A | B)
    if not combined:
        return []

    largest_set = []
    for group in group_with_gaps(combined, max_gaps):
        if any(x in A for x in group) and any(x in B for x in group):
            if len(group) > len(largest_set):
                largest_set = group

    return largest_set

