from PIL import Image
import time
from mazes import Maze
from factory import SolverFactory
Image.MAX_IMAGE_PIXELS = None

# Read command line arguments - the python argparse class is convenient here.
import argparse

def solve(factory, method, input_file, output_file, visualize_enabled=False, csv_path=None):
    # Load Image
    print ("Loading Image")
    im = Image.open(input_file)
    if visualize_enabled:
        import visualize
        viz = visualize.init(im)

    # Create the maze (and time it) - for many mazes this is more time consuming than solving the maze
    print ("Creating Maze")
    t0 = time.time()
    maze = Maze(im)
    t1 = time.time()
    print ("Node Count:", maze.count)
    total = t1-t0
    print ("Time elapsed:", total, "\n")

    # Create and run solver
    [title, solver] = factory.createsolver(method)
    print ("Starting Solve:", title)

    t0 = time.time()
    [result, stats] = solver(maze)
    t1 = time.time()

    total = t1-t0

    # Print solve stats
    print ("Nodes explored: ", stats[0])
    if (stats[2]):
        print ("Path found, length", stats[1])
    else:
        print ("No Path Found")
    print ("Time elapsed: ", total, "\n")

    """
    Create and save the output image.
    This is simple drawing code that travels between each node in turn, drawing either
    a horizontal or vertical line as required. Line colour is roughly interpolated between
    blue and red depending on how far down the path this section is.
    """

    print ("Saving Image")
    im = im.convert('RGB')
    impixels = im.load()

    resultpath = [n.Position for n in result]

    length = len(resultpath)

    for i in range(0, length - 1):
        a = resultpath[i]
        b = resultpath[i+1]

        # Blue - red
        r = int((i / length) * 255)
        px = (r, 0, 255 - r)

        if a[0] == b[0]:
            # Ys equal - horizontal line
            for x in range(min(a[1],b[1]), max(a[1],b[1])):
                impixels[x,a[0]] = px
                if visualize_enabled:
                    visualize.draw_path_segment(a, (a[0], x))
        elif a[1] == b[1]:
            # Xs equal - vertical line
            for y in range(min(a[0],b[0]), max(a[0],b[0]) + 1):
                impixels[a[1],y] = px
                if visualize_enabled:
                    visualize.draw_path_segment(a, (y, a[1]))

    im.save(output_file)
    if visualize_enabled:
        visualize.finish()

    # CSV logging (append)
    if csv_path != None:
        try:
            import csv, os
            exists = os.path.exists(csv_path)
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if not exists:
                    writer.writerow(["timestamp","method","title","input","output","width","height","nodes_in_graph","nodes_explored","path_len","completed","maze_build_seconds","solve_seconds"]) 
                writer.writerow([
                    int(time.time()),
                    method,
                    title,
                    input_file,
                    output_file,
                    maze.width,
                    maze.height,
                    maze.count,
                    stats[0],
                    stats[1],
                    1 if stats[2] else 0,
                    round(total + 0.0, 6), # deprecated: leaving only solve_seconds below
                    round(total, 6)
                ])
        except Exception as e:
            print ("CSV logging failed:", str(e))


def main():
    sf = SolverFactory()
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--method", nargs='?', const=sf.Default, default=sf.Default,
                        choices=sf.Choices)
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("-v", "--visualize", action='store_true', help="Enable live visualization")
    parser.add_argument("--csv", dest='csv_path', default=None, help="Append run metrics to CSV path")
    args = parser.parse_args()

    solve(sf, args.method, args.input_file, args.output_file, visualize_enabled=args.visualize, csv_path=args.csv_path)

if __name__ == "__main__":
    main()

