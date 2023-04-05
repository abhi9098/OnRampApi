from flask import session

def create_flows():
      dict_ = session.pop('flows', None)
      flow= """  <Flow name="GetIP">
    <Description>{2}</Description>
    <Request/>
    <Response/>
    <Condition>(proxy.pathsuffix MatchesPath "{0}") and (request.verb = "{1}")</Condition>
   </Flow>"""
      output = ""
      for key, values in dict_.items():
            for i in range(len(values[0])):
                  output += flow.format(key, values[0][i], values[1][i]) + "\n"

      flows=f"""<Flows>
      {output}</Flows>"""
      return flows