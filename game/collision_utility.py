import pygame

"""
Class created using code from https://www.pygame.org/wiki/IntersectingLineDetection
Mathematic explanation: https://www.mathopenref.com/coordintersection.html
"""
class CollisionUtility:

    @staticmethod
    def check_lander_collision_with_surface(lander, surface):
        lander_bottom_line = (lander.rect.bottomleft, lander.rect.bottomright)
        lander_top_line = (lander.rect.topleft, lander.rect.topright)
        lander_left_line = (lander.rect.topleft, lander.rect.bottomleft)
        lander_right_line = (lander.rect.topright, lander.rect.bottomright)
        lines = (lander_bottom_line, lander_top_line, lander_left_line, lander_right_line)

        surface_points = CollisionUtility.surface_points_below_lander(lander, surface)

        intersection_point_found = False

        for i in range(len(surface_points)-1):
            points = [surface_points[i], surface_points[i+1]]
            get_intersection = lambda line: CollisionUtility.calculate_intersect_point(line[0], line[1], points[0], points[1])
            intersections = list(map(get_intersection, lines))

            if any(intersections):
                intersection_point_found = True
                break

        if not intersection_point_found:
            lowest_lander_point = max(lander_bottom_line[0][1], lander_bottom_line[1][1], lander_top_line[0][1], lander_top_line[1][1])
            lowest_surface_point = 0
            for p in surface_points:
                lowest_surface_point = max(lowest_surface_point, p[1])
            intersection_point_found = lowest_surface_point < lowest_lander_point

        return intersection_point_found

    @staticmethod
    def calculate_gradient(p1, p2):
        """Calc the gradient 'm' of a line between p1 and p2"""
        # Ensure that the line is not vertical
        if p1[0] == p2[0]:
            return None
        m = (p1[1] - p2[1]) / (p1[0] - p2[0])
        return m

    @staticmethod
    def calculate_y_axis_intersect(p, m):
        """Calc the point 'b' where line crosses the Y axis"""
        return p[1] - (m * p[0])

    @staticmethod
    def calculate_not_parallel_intersection(points, gradients):
        p1, p2, p3, p4 = points
        m1, m2 = gradients
        # See if either line is vertical
        if m1 is not None and m2 is not None:
            # Neither line vertical
            b1 = CollisionUtility.calculate_y_axis_intersect(p1, m1)
            b2 = CollisionUtility.calculate_y_axis_intersect(p3, m2)
            x = (b2 - b1) / (m1 - m2)
            y = (m1 * x) + b1
        else:
            if m1 is None:
                b2 = CollisionUtility.calculate_y_axis_intersect(p3, m2)
                x = p1[0]
                y = (m2 * x) + b2
            # Line 2 is vertical so use line 1's values
            elif m2 is None:
                b1 = CollisionUtility.calculate_y_axis_intersect(p1, m1)
                x = p3[0]
                y = (m1 * x) + b1
            else:
                assert False
        point = x, y
        return point,

    @staticmethod
    def calculate_parallel_intersection(points, gradients):
        """
        Parallel lines with same 'b' value must be the same line so they intersect
        everywhere in this case we return the start and end points of both lines
        the calculate_intersect_point method will sort out which of these points
        lays on both line segments
        """
        p1, p2, p3, p4 = points
        m1, m2 = gradients
        b1, b2 = None, None # vertical lines have no b value
        if m1 is not None:
            b1 = CollisionUtility.calculate_y_axis_intersect(p1, m1)
        if m2 is not None:
            b2 = CollisionUtility.calculate_y_axis_intersect(p3, m2)
        # If these parallel lines lay on one another
        return (p1, p2, p3, p4) if b1 == b2 else None

    @staticmethod
    def getIntersectPoint(p1, p2, p3, p4):
        """
        Calc the point where two infinitely long lines (p1 to p2 and p3 to p4) intersect.
        Handle parallel lines and vertical lines (the later has infinate 'm').
        """
        points = p1, p2, p3, p4
        gradients = (
            CollisionUtility.calculate_gradient(p1, p2), CollisionUtility.calculate_gradient(p3, p4)
        )

        # See if the the lines are parallel
        if gradients[0] != gradients[1]:
            return CollisionUtility.calculate_not_parallel_intersection(points, gradients)
        else:
            return CollisionUtility.calculate_parallel_intersection(points, gradients)

    @staticmethod
    def create_rect(points):
        p1, p2 = points
        width = p2[0] - p1[0]
        height = p2[1] - p1[1]
        rect = pygame.Rect(p1, (width , height))
        rect.normalize()
        rect.width = max(rect.width, 1)
        rect.height = max(rect.height, 1)
        return rect

    @staticmethod
    def calculate_intersect_point(p1, p2, p3, p4):
        """
        For line segments (ie not infinitely long lines) the intersect point
        may not lay on both lines.
        """
        p = CollisionUtility.getIntersectPoint(p1, p2, p3, p4)
        if p is not None:
            points_arr = ((p1, p2), (p3, p4))
            r1, r2 = list(map(CollisionUtility.create_rect, points_arr))
            for point in p:
                try:
                    res1 = r1.collidepoint(point)
                    res2 = r2.collidepoint(point)
                    if res1 and res2:
                        point = [int(pp) for pp in point]
                        return point
                except:
                    str = "point was invalid  ", point
                    print(str)
        return None

    @staticmethod
    def surface_points_below_lander(lander, surface):
        lander_leftmost_point = lander.rect.bottomleft[0]
        lander_rightmost_point = lander.rect.bottomright[0]
        points_below_lander = []
        leftmost_point_found = False
        rightmost_point_found = False
        for i in range(len(surface.polygon_points)-1):
            if not leftmost_point_found:
                p = surface.polygon_points[i]
                p1 = surface.polygon_points[i+1]
                if p[0] <= lander_leftmost_point and p1[0] > lander_leftmost_point:
                    points_below_lander.append(p)
                    leftmost_point_found = True
            elif not rightmost_point_found:
                p = surface.polygon_points[i]
                points_below_lander.append(p)
                if p[0] >= lander_rightmost_point:
                    rightmost_point_found = True
        return points_below_lander

    @staticmethod
    def check_gameobject_window_collision(gameobject, screen_dimensions):
        gameobject_leftmost_point = gameobject.rect.topleft[0]
        gameobject_rightmost_point = gameobject.rect.topright[0]
        gameobject_bottommost_point = gameobject.rect.bottomleft[1]
        return gameobject_rightmost_point < 0 or \
            gameobject_leftmost_point > screen_dimensions[0] or \
            gameobject_bottommost_point < 0
