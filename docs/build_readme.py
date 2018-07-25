import os
import sys
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.split(curr_dir)[0])


if __name__ == "__main__":

    with open('docs/_readme_template.md') as f:
        template = f.read()
    with open('examples/_usage.py') as u:
        usage = u.read()

    readme_usage, do_append = [], False
    for line in usage.splitlines():
        if line.startswith('#') and line.endswith('<<from_here'):
            do_append = True
            continue
        if line.startswith('#') and line.endswith('>>to_here'):
            do_append = False

        if do_append:
            readme_usage.append(line)

    readme = template.format(
        tmpl_usage_examples='\n'.join(readme_usage)
    )

    with open('README.md', 'w') as rd:
        rd.write(readme)
